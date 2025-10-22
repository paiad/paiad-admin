package paiad.handler;

import cn.dev33.satoken.exception.NotLoginException;
import cn.dev33.satoken.util.SaResult;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.validation.BindException;
import org.springframework.validation.FieldError;
import jakarta.validation.ConstraintViolationException;
import org.springframework.web.bind.MethodArgumentNotValidException;

/**
 *  登录异常捕获
 *  401 警告
 * */
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(NotLoginException.class)
    public SaResult handleNotLoginException(NotLoginException e) {
        String message = switch (e.getType()) {
            case NotLoginException.NOT_TOKEN -> "未提供 Token";
            case NotLoginException.INVALID_TOKEN -> "无效的 Token";
            case NotLoginException.TOKEN_TIMEOUT -> "Token 已过期";
            default -> "当前会话未登录";
        };
        return SaResult.error(message).setCode(401);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public SaResult handleMethodArgumentNotValid(MethodArgumentNotValidException e) {
        FieldError fieldError = e.getBindingResult().getFieldError();
        String message = fieldError != null ? fieldError.getDefaultMessage() : "请求参数校验失败";
        return SaResult.error(message).setCode(400);
    }

    @ExceptionHandler(BindException.class)
    public SaResult handleBindException(BindException e) {
        FieldError fieldError = e.getBindingResult().getFieldError();
        String message = fieldError != null ? fieldError.getDefaultMessage() : "请求参数绑定失败";
        return SaResult.error(message).setCode(400);
    }

    @ExceptionHandler(ConstraintViolationException.class)
    public SaResult handleConstraintViolation(ConstraintViolationException e) {
        String message = e.getConstraintViolations().stream()
                .findFirst()
                .map(v -> v.getMessage())
                .orElse("参数约束违反");
        return SaResult.error(message).setCode(400);
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public SaResult handleIllegalArgument(IllegalArgumentException e) {
        return SaResult.error(e.getMessage()).setCode(400);
    }

    @ExceptionHandler(Exception.class)
    public SaResult handleGenericException(Exception e) {
        return SaResult.error("服务内部错误").setCode(500);
    }
}
