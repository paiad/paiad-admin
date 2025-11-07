package paiad.web;

import jakarta.servlet.http.HttpServletRequest;
import paiad.util.IpUtils;

/**
 * Web 层工具封装，面向 server 暴露统一 API。
 * 内部使用 common 模块的 IpUtils，避免 server 直接依赖 common 的类。
 */
public final class WebUtils {
    private WebUtils() {}

    /**
     * 获取客户端真实 IP，兼容常见反向代理场景。
     */
    public static String getClientIp(HttpServletRequest request) {
        return IpUtils.getClientIp(request);
    }
}