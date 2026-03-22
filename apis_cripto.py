import os
from typing import Any, Dict, Optional, Union

import requests
from dotenv import load_dotenv

load_dotenv()

JsonResponse = Union[Dict[str, Any], list, float, int, str]


class APIConfigError(Exception):
    def __init__(
        self,
        message: str,
        service: Optional[str] = None,
        env_var: Optional[str] = None,
    ) -> None:
        self.message = message
        self.service = service
        self.env_var = env_var

        details = [message]
        if service:
            details.append(f"service={service}")
        if env_var:
            details.append(f"env_var={env_var}")

        super().__init__(" | ".join(details))

    def __str__(self) -> str:
        return self.args[0]


class APIRequestError(Exception):
    def __init__(
        self,
        message: str,
        service: Optional[str] = None,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
    ) -> None:
        self.message = message
        self.service = service
        self.url = url
        self.status_code = status_code
        self.response_text = response_text

        details = [message]
        if service:
            details.append(f"service={service}")
        if url:
            details.append(f"url={url}")
        if status_code is not None:
            details.append(f"status_code={status_code}")
        if response_text:
            details.append(f"response={response_text[:300]}")

        super().__init__(" | ".join(details))

    def __str__(self) -> str:
        return self.args[0]


class BaseAPIClient:
    def __init__(self, service_name: str, timeout_env: str = "REQUEST_TIMEOUT") -> None:
        self.service_name = service_name
        self.timeout = int(os.getenv(timeout_env, "20"))
        self.user_agent = os.getenv("HTTP_USER_AGENT", "CriptoBot/1.0")

        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        })

    def _request(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> JsonResponse:
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=self.timeout,
            )
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return response.json()

            text = response.text.strip()
            try:
                return response.json()
            except ValueError:
                try:
                    return float(text)
                except ValueError:
                    return text

        except requests.HTTPError as e:
            raise APIRequestError(
                message=f"Erro HTTP na API {self.service_name}",
                service=self.service_name,
                url=url,
                status_code=e.response.status_code if e.response else None,
                response_text=e.response.text if e.response else None,
            ) from e
        except requests.RequestException as e:
            raise APIRequestError(
                message=f"Erro de requisição na API {self.service_name}",
                service=self.service_name,
                url=url,
            ) from e


class DefiLlamaAPI(BaseAPIClient):
    def __init__(self) -> None:
        super().__init__("defillama")
        self.base_url = os.getenv(
            "DEFILLAMA_BASE_URL", "https://pro-api.llama.fi").rstrip("/")
        self.api_key = os.getenv("DEFILLAMA_API_KEY", "").strip()

    def _build_url(self, endpoint: str, pro: bool = False) -> str:
        endpoint = endpoint.lstrip("/")
        if pro:
            if not self.api_key:
                raise APIConfigError(
                    message="DEFILLAMA_API_KEY não configurada para endpoint Pro",
                    service="defillama",
                    env_var="DEFILLAMA_API_KEY",
                )
            return f"{self.base_url}/{self.api_key}/{endpoint}"
        return f"{self.base_url}/{endpoint}"

    def _llama_request(
        self,
        method: str,
        endpoint: str,
        *,
        pro: bool = False,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> JsonResponse:
        url = self._build_url(endpoint, pro=pro)
        return self._request(method, url, params=params, json_body=json_body)

    def protocols(self) -> JsonResponse:
        return self._llama_request("GET", "/api/protocols")

    def protocol(self, protocol_slug: str) -> JsonResponse:
        return self._llama_request("GET", f"/api/protocol/{protocol_slug}")

    def protocol_tvl(self, protocol_slug: str) -> JsonResponse:
        return self._llama_request("GET", f"/api/tvl/{protocol_slug}")

    def chains(self) -> JsonResponse:
        return self._llama_request("GET", "/api/v2/chains")

    def historical_chain_tvl_all(self) -> JsonResponse:
        return self._llama_request("GET", "/api/v2/historicalChainTvl")

    def historical_chain_tvl(self, chain: str) -> JsonResponse:
        return self._llama_request("GET", f"/api/v2/historicalChainTvl/{chain}")

    def current_prices(self, coins: str, search_width: Optional[str] = None) -> JsonResponse:
        params = {}
        if search_width:
            params["searchWidth"] = search_width
        return self._llama_request("GET", f"/coins/prices/current/{coins}", params=params)

    def historical_prices(self, timestamp: int, coins: str, search_width: Optional[str] = None) -> JsonResponse:
        params = {}
        if search_width:
            params["searchWidth"] = search_width
        return self._llama_request("GET", f"/coins/prices/historical/{timestamp}/{coins}", params=params)

    def batch_historical_prices(self, coins_map: Dict[str, list[int]]) -> JsonResponse:
        return self._llama_request("POST", "/coins/batchHistorical", json_body={"coins": coins_map})

    def coin_chart(
        self,
        coins: str,
        period: Optional[str] = None,
        span: Optional[int] = None,
        search_width: Optional[str] = None,
    ) -> JsonResponse:
        params = {}
        if period:
            params["period"] = period
        if span is not None:
            params["span"] = span
        if search_width:
            params["searchWidth"] = search_width
        return self._llama_request("GET", f"/coins/chart/{coins}", params=params)

    def first_price(self, coins: str) -> JsonResponse:
        return self._llama_request("GET", f"/coins/prices/first/{coins}")

    def stablecoins(self) -> JsonResponse:
        return self._llama_request("GET", "/stablecoins/stablecoins")

    def stablecoin_chains(self) -> JsonResponse:
        return self._llama_request("GET", "/stablecoins/stablecoinchains")

    def stablecoin_prices(self) -> JsonResponse:
        return self._llama_request("GET", "/stablecoins/stablecoinprices")

    def overview_dexs(self, data_type: Optional[str] = None) -> JsonResponse:
        params = {}
        if data_type:
            params["dataType"] = data_type
        return self._llama_request("GET", "/api/overview/dexs", params=params)

    def overview_fees(self, data_type: Optional[str] = None) -> JsonResponse:
        params = {}
        if data_type:
            params["dataType"] = data_type
        return self._llama_request("GET", "/api/overview/fees", params=params)

    def yields_pools(self) -> JsonResponse:
        return self._llama_request("GET", "/yields/pools", pro=True)

    def yield_chart(self, pool_id: str) -> JsonResponse:
        return self._llama_request("GET", f"/yields/chart/{pool_id}", pro=True)

    def bridges(self, include_chains: Optional[bool] = None) -> JsonResponse:
        params = {}
        if include_chains is not None:
            params["includeChains"] = str(include_chains).lower()
        return self._llama_request("GET", "/bridges/bridges", pro=True, params=params)


class CoinMarketCapAPI(BaseAPIClient):
    def __init__(self) -> None:
        super().__init__("coinmarketcap")
        self.base_url = os.getenv(
            "CMC_BASE_URL", "https://pro-api.coinmarketcap.com").rstrip("/")
        self.api_key = os.getenv("CMC_API_KEY", "").strip()

    def _cmc_headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise APIConfigError(
                message="CMC_API_KEY não configurada",
                service="coinmarketcap",
                env_var="CMC_API_KEY",
            )
        return {"X-CMC_PRO_API_KEY": self.api_key}

    def quotes_latest(self, symbol: str, convert: str = "USD") -> JsonResponse:
        url = f"{self.base_url}/v2/cryptocurrency/quotes/latest"
        params = {"symbol": symbol.upper(), "convert": convert.upper()}
        return self._request("GET", url, headers=self._cmc_headers(), params=params)

    def metadata(self, symbol: str) -> JsonResponse:
        url = f"{self.base_url}/v2/cryptocurrency/info"
        params = {"symbol": symbol.upper()}
        return self._request("GET", url, headers=self._cmc_headers(), params=params)

    def listings_latest(self, limit: int = 100, convert: str = "USD") -> JsonResponse:
        url = f"{self.base_url}/v1/cryptocurrency/listings/latest"
        params = {"limit": limit, "convert": convert.upper()}
        return self._request("GET", url, headers=self._cmc_headers(), params=params)


class DexScreenerAPI(BaseAPIClient):
    def __init__(self) -> None:
        super().__init__("dexscreener")
        self.base_url = os.getenv(
            "DEXSCREENER_BASE_URL", "https://api.dexscreener.com").rstrip("/")

    def search_pairs(self, query: str) -> JsonResponse:
        url = f"{self.base_url}/latest/dex/search"
        return self._request("GET", url, params={"q": query})

    def token_pairs(self, token_address: str) -> JsonResponse:
        url = f"{self.base_url}/latest/dex/tokens/{token_address}"
        return self._request("GET", url)

    def pair_by_chain(self, chain_id: str, pair_address: str) -> JsonResponse:
        url = f"{self.base_url}/latest/dex/pairs/{chain_id}/{pair_address}"
        return self._request("GET", url)


class CriptoAPIs:
    def __init__(self) -> None:
        self.defillama = DefiLlamaAPI()
        self.coinmarketcap = CoinMarketCapAPI()
        self.dexscreener = DexScreenerAPI()
