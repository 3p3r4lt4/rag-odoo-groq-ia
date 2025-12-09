import httpx
import json
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class OdooClient:
    """Cliente para APIs de Odoo - Versión simplificada"""
    
    def __init__(self):
        self.timeout = 30.0
        
    async def consultar_servicios(self, company_id: str, service_id: str) -> Dict[str, Any]:
        """Consulta servicios en Odoo"""
        from config.settings import settings
        
        url = f"{settings.odoo_api_base_url}/sojo/api/v1/ConsultaServicios"
        
        headers = {
            "Content-type": "application/json",
            "token": settings.odoo_api_token_servicios,
        }
        
        data = {
            "company_id": company_id,
            "service_id": service_id
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Consultando servicio {service_id} en {url}")
                response = await client.post(url, headers=headers, json=data)
                
                # Log de respuesta para debug
                logger.info(f"Status: {response.status_code}, Respuesta: {response.text[:200]}")
                
                response.raise_for_status()
                result = response.json()
                
                # Verificar estructura de respuesta
                if not isinstance(result, dict):
                    return {"error": "Respuesta no es JSON válido", "success": False}
                
                # Asegurar que tiene campo success
                if "success" not in result:
                    result["success"] = True  # Asumir éxito si no hay campo
                    
                return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            return {"error": f"HTTP {e.response.status_code}", "success": False}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return {"error": "Respuesta no es JSON válido", "success": False}
        except Exception as e:
            logger.error(f"Error consultando servicios: {e}")
            return {"error": str(e), "success": False}
    
    async def listar_contratos(self, company_id: str, number_identification: str) -> Dict[str, Any]:
        """Lista contratos de un cliente"""
        from config.settings import settings
        
        url = f"{settings.odoo_api_base_url}/Contact/api/v1/DetailContract"
        
        headers = {
            "Content-Type": "application/json",
            "token": settings.odoo_api_token_contratos,
            "Cookie": "session_id=808254928910e2da70c349ca2b3d9aec2a33ba66"
        }
        
        data = {
            "company_id": company_id,
            "number_identification": number_identification
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error listando contratos: {e}")
            return {"error": str(e), "success": False}
    
    async def consultar_deuda_bcp(self, customer_id: str, currency: str = "PEN") -> Dict[str, Any]:
        """Consulta deuda en BCP"""
        from config.settings import settings
        
        url = f"{settings.bcp_api_url}/ConsultarDeuda"
        service_id = "1001" if currency.upper() == "PEN" else "1002"
        
        headers = {
            "Content-type": "application/json",
            "Cookie": "session_id=2001d21ad8b5e8fdc798e117fc43a710479df8dc"
        }
        
        data = {
            "rqUUID": "550e8400-e29b-41d4-a716-446655440000",
            "operationDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "operationNumber": "01234567",
            "financialEntity": "002",
            "channel": "IB",
            "serviceId": service_id,
            "customerId": customer_id
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error consultando deuda BCP: {e}")
            return {"error": str(e), "success": False}
    
    def format_response(self, data: Dict[str, Any], query_type: str) -> str:
        """Formatea respuesta para Telegram"""
        if not data.get("success", False):
            error_msg = data.get('error', 'Error desconocido')
            return f"❌ *Error en la consulta*\n\n`{str(error_msg)[:200]}`"
        
        try:
            if query_type == "servicio":
                return self._format_service(data)
            elif query_type == "contrato":
                return self._format_contract(data)
            elif query_type == "deuda":
                return self._format_debt(data)
            else:
                # Formato genérico
                return f"📊 *Datos recibidos:*\n```json\n{json.dumps(data, indent=2, ensure_ascii=False)[:1500]}\n```"
        except Exception as e:
            return f"✅ *Consulta exitosa*\n\n`Datos crudos: {str(data)[:300]}...`"
    
    def _format_service(self, data: Dict[str, Any]) -> str:
        """Formatea respuesta de servicio - VERSIÓN CORREGIDA"""
        try:
            # La API devuelve: {"jsonrpc": "2.0", "id": null, "result": {...}}
            # Extraer los datos del campo 'result'
            result_data = data.get("result", {})
            
            if not result_data:
                # Intentar otras posibles ubicaciones
                result_data = data.get("data", data.get("response", data))
            
            if isinstance(result_data, dict) and result_data:
                # Filtrar campos técnicos y mostrar solo información relevante
                lines = ["✅ *Información del Servicio*", ""]
                
                # Campos importantes a mostrar (en orden)
                important_fields = [
                    "name", "number_identification", "status_service",
                    "partner_street", "state", "product_id", "category",
                    "seller", "collection", "medio", "transporte"
                ]
                
                for field in important_fields:
                    if field in result_data and result_data[field]:
                        # Traducir nombres de campos para mejor legibilidad
                        field_names = {
                            "name": "Cliente",
                            "number_identification": "RUC/DNI",
                            "status_service": "Estado",
                            "partner_street": "Dirección",
                            "state": "Departamento",
                            "product_id": "Producto",
                            "category": "Categoría",
                            "seller": "Vendedor",
                            "collection": "Cobranza",
                            "medio": "Medio",
                            "transporte": "Transporte"
                        }
                        
                        display_name = field_names.get(field, field)
                        lines.append(f"• *{display_name}:* `{result_data[field]}`")
                
                return "\n".join(lines)
            else:
                # Si no es dict o está vacío
                return f"✅ *Consulta exitosa*\n\n`{str(data)[:500]}`"
                
        except Exception as e:
            logger.error(f"Error formateando servicio: {e}")
            return f"✅ *Servicio consultado*\n\n`{json.dumps(data, ensure_ascii=False)[:500]}`"
    
    def _format_contract(self, data: Dict[str, Any]) -> str:
        """Formatea respuesta de contrato"""
        try:
            contracts = data.get("data", data.get("contracts", []))
            if not contracts:
                return "📭 *No se encontraron contratos*"
            
            if isinstance(contracts, list):
                response = ["📄 *Contratos Encontrados*", ""]
                
                for i, contract in enumerate(contracts[:3], 1):  # Máximo 3
                    if isinstance(contract, dict):
                        response.append(f"*Contrato {i}:*")
                        # Mostrar campos comunes
                        for key in ["contract_id", "client_name", "status", "start_date"]:
                            if key in contract:
                                response.append(f"  • *{key}:* `{contract[key]}`")
                        response.append("")
                
                if len(contracts) > 3:
                    response.append(f"*... y {len(contracts) - 3} más*")
                
                return "\n".join(response)
            else:
                return f"📄 *Contratos*\n\n`{str(contracts)[:500]}`"
                
        except Exception as e:
            return f"📄 *Contratos consultados*\n\n`{json.dumps(data, ensure_ascii=False)[:500]}`"
    
    def _format_debt(self, data: Dict[str, Any]) -> str:
        """Formatea respuesta de deuda"""
        try:
            debt_data = data.get("data", data.get("debt", data))
            
            if isinstance(debt_data, dict):
                lines = ["💰 *Información de Deuda*", ""]
                
                for key, value in list(debt_data.items())[:8]:  # Mostrar primeros 8 campos
                    if isinstance(value, (str, int, float, bool)) and value:
                        lines.append(f"• *{key}:* `{value}`")
                
                return "\n".join(lines)
            else:
                return f"💰 *Deuda consultada*\n\n`{str(debt_data)[:500]}`"
                
        except Exception as e:
            return f"💰 *Deuda consultada*\n\n`{json.dumps(data, ensure_ascii=False)[:500]}`"
