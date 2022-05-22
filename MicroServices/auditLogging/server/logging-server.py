from concurrent import futures

import grpc
from grpc_interceptor import ExceptionToStatusInterceptor
from pymongo import MongoClient
from datetime import datetime

from logging_pb2 import (
    Log,
    Empty
)
import logging_pb2_grpc

client = MongoClient('mongo', 27017 ,username='admin', password='admin')
logs = client["steam"]
db = logs["logs"]

class LoggingService(logging_pb2_grpc.LoggingServicer):
    def StoreLog(self, request, context):
        db.insert_one({
            "operation": request.operation,
            "endpoint": request.endpoint,
            "status": request.status,
            "service": request.service,
            "remote_addr": request.addr,
            "user": "default",
            "host": request.host,
            "date": request.date
        })
        return Empty()

def serve():
    interceptors = [ExceptionToStatusInterceptor()]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )
    logging_pb2_grpc.add_LoggingServicer_to_server(
        LoggingService(), server
    )

    server.add_insecure_port("[::]:50160")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()