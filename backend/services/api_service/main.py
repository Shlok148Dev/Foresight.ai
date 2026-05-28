from fastapi import FastAPI, HTTPException
import grpc
try:
    from app.services.grpc_service_pb2 import TrendRequest, ForecastRequest
    from app.services.grpc_service_pb2_grpc import TrendServiceStub
except ImportError:
    pass

app = FastAPI(title="API Service")

# Mock gRPC setup for local dev without grpc running
try:
    forecast_channel = grpc.aio.secure_channel('forecast-service:50051', grpc.ssl_channel_credentials())
    forecast_stub = TrendServiceStub(forecast_channel)
except Exception:
    forecast_stub = None

@app.get("/trends/{trend_id}")
async def get_trend(trend_id: str):
    try:
        if not forecast_stub:
            return {"trend_id": trend_id, "mock": True}
        request = TrendRequest(trend_id=trend_id)
        response = await forecast_stub.GetTrend(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trends/{trend_id}/forecast")
async def get_forecast(trend_id: str):
    try:
        if not forecast_stub:
            return {"trend_id": trend_id, "forecast": "mock", "mock": True}
        request = ForecastRequest(trend_id=trend_id)
        response = await forecast_stub.ForecastTrend(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "api-service"}
