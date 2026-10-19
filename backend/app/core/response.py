"""
响应格式化组件
"""
from typing import Optional, Any, Dict
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi import status


class ResponseModel:
    """统一响应模型"""
    
    def __init__(
        self,
        code: int = 200,
        message: str = "success",
        data: Optional[Any] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        初始化响应模型
        
        Args:
            code: 响应代码
            message: 响应消息
            data: 响应数据
            timestamp: 时间戳
        """
        self.code = code
        self.message = message
        self.data = data
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 响应字典
        """
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }


def success_response(
    data: Optional[Any] = None,
    message: str = "success",
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """
    成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        status_code: HTTP状态码
    
    Returns:
        JSONResponse: JSON响应对象
    """
    response = ResponseModel(
        code=200,
        message=message,
        data=data
    )
    return JSONResponse(
        status_code=status_code,
        content=response.to_dict()
    )


def error_response(
    message: str = "error",
    code: int = 500,
    details: Optional[Dict[str, Any]] = None,
    status_code: Optional[int] = None
) -> JSONResponse:
    """
    错误响应
    
    Args:
        message: 错误消息
        code: 错误代码
        details: 错误详情
        status_code: HTTP状态码（如果不提供，根据code自动映射）
    
    Returns:
        JSONResponse: JSON响应对象
    """
    if status_code is None:
        # 根据错误代码映射HTTP状态码
        status_code_map = {
            400: status.HTTP_400_BAD_REQUEST,
            401: status.HTTP_401_UNAUTHORIZED,
            403: status.HTTP_403_FORBIDDEN,
            404: status.HTTP_404_NOT_FOUND,
            422: status.HTTP_422_UNPROCESSABLE_ENTITY,
            500: status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
        status_code = status_code_map.get(code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    response = ResponseModel(
        code=code,
        message=message,
        data={"details": details} if details else None
    )
    return JSONResponse(
        status_code=status_code,
        content=response.to_dict()
    )


def created_response(
    data: Optional[Any] = None,
    message: str = "created successfully"
) -> JSONResponse:
    """
    创建成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
    
    Returns:
        JSONResponse: JSON响应对象
    """
    return success_response(data=data, message=message, status_code=status.HTTP_201_CREATED)


def paginated_response(
    items: list,
    total: int,
    page: int = 1,
    page_size: int = 10,
    message: str = "success"
) -> JSONResponse:
    """
    分页响应
    
    Args:
        items: 数据列表
        total: 总记录数
        page: 当前页码
        page_size: 每页大小
        message: 响应消息
    
    Returns:
        JSONResponse: JSON响应对象
    """
    data = {
        "items": items,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size if page_size > 0 else 0
        }
    }
    return success_response(data=data, message=message)

