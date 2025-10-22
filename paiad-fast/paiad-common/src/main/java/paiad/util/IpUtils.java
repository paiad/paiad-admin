package paiad.util;

import jakarta.servlet.http.HttpServletRequest;
import org.apache.commons.lang3.StringUtils;

import java.util.Arrays;
import java.util.List;

/**
 * 获取客户端真实 IP 的工具类，支持常见反向代理场景。
 */
public final class IpUtils {
    private IpUtils() {}

    private static final List<String> HEADER_CANDIDATES = Arrays.asList(
            "x-forwarded-for",
            "X-Forwarded-For",
            "X-Real-IP",
            "X-Forwarded-Host",
            "Proxy-Client-IP",
            "WL-Proxy-Client-IP",
            "HTTP_CLIENT_IP",
            "HTTP_X_FORWARDED_FOR"
    );

    public static String getClientIp(HttpServletRequest request) {
        for (String header : HEADER_CANDIDATES) {
            String ip = request.getHeader(header);
            if (StringUtils.isNotBlank(ip) && !"unknown".equalsIgnoreCase(ip)) {
                // 反向代理可能存在多个 IP，以逗号分隔，取第一个有效值
                int commaIndex = ip.indexOf(',');
                return commaIndex > 0 ? ip.substring(0, commaIndex).trim() : ip.trim();
            }
        }
        String ip = request.getRemoteAddr();
        return ip == null ? "" : ip;
    }
}
