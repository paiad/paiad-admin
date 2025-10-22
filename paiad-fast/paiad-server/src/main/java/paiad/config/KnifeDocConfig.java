package paiad.config;

import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.net.InetAddress;
import java.net.NetworkInterface;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.List;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import io.swagger.v3.oas.models.servers.Server;

/**
 * 统一 Knife4j / OpenAPI 文档配置：
 * - 设置基础 Info（标题、描述、版本、联系人、许可）
 * - 配置全局安全方案（与 Sa-Token 的 header 一致）
 * - 输出本机及局域网可访问的文档地址（doc.html）
 */
@Configuration
@Slf4j
public class KnifeDocConfig {

    @Value("${server.port:8080}")
    private String port;

    @Value("${server.servlet.context-path:}")
    private String contextPath;

    @Value("${sa-token.token-name:paiad-token}")
    private String tokenHeaderName;

    private static final String STAR = "\uD83C\uDF1F --> ";
    private static final String DOC_PATH = "/doc.html";

    /**
     * 定义 OpenAPI 文档基础信息与全局安全方案。
     */
    @Bean
    public OpenAPI openAPI() {
        // 基础信息
        Info info = new Info()
                .title("Paiad 后端接口文档")
                .description("统一的后端 API 文档，包含认证、MQTT 等模块")
                .version("v1.0")
                .contact(new Contact().name("Paiad Team").email("support@paiad.local"))
                .license(new License().name("MIT"));

        // 与 Sa-Token 对齐的安全方案（请求头传递 token）
        SecurityScheme tokenScheme = new SecurityScheme()
                .type(SecurityScheme.Type.APIKEY)
                .in(SecurityScheme.In.HEADER)
                .name(tokenHeaderName)
                .description("在请求头中携带 " + tokenHeaderName + " 进行鉴权");

        Components components = new Components()
                .addSecuritySchemes(tokenHeaderName, tokenScheme);

        // 默认应用到所有接口的 SecurityRequirement
        SecurityRequirement requirement = new SecurityRequirement()
                .addList(tokenHeaderName);

        // 服务器地址（包含 localhost 与局域网 IP）
        List<Server> servers = new ArrayList<>();
        String basePath = normalizeContextPath(contextPath);
        servers.add(new Server().url("http://localhost:" + port + basePath).description("本机"));
        for (String ip : getAllIpAddresses()) {
            servers.add(new Server().url("http://" + ip + ":" + port + basePath).description("局域网"));
        }

        return new OpenAPI()
                .info(info)
                .components(components)
                .addSecurityItem(requirement)
                .servers(servers);
    }

    /**
     * 启动时输出文档访问地址。
     */
    @PostConstruct
    public void printDocUrls() {
        String basePath = normalizeContextPath(contextPath);
        StringBuilder sb = new StringBuilder();
        sb.append("\n---------------------------------------------------\n");
        sb.append("Knife4j 文档地址:\n");
        sb.append(STAR).append("http://localhost:")
                .append(port).append(basePath).append(DOC_PATH).append("\n");
        for (String ip : getAllIpAddresses()) {
            sb.append(STAR).append("http://").append(ip).append(":")
                    .append(port).append(basePath).append(DOC_PATH).append("\n");
        }
        sb.append("---------------------------------------------------");
        log.info(sb.toString());
    }

    private String normalizeContextPath(String ctx) {
        if (ctx == null || ctx.isBlank()) {
            return "";
        }
        return ctx.startsWith("/") ? ctx : "/" + ctx;
    }

    private List<String> getAllIpAddresses() {
        List<String> ipList = new ArrayList<>();
        try {
            Enumeration<NetworkInterface> networkInterfaces = NetworkInterface.getNetworkInterfaces();
            while (networkInterfaces.hasMoreElements()) {
                NetworkInterface networkInterface = networkInterfaces.nextElement();
                if (!networkInterface.isUp() || networkInterface.isLoopback()) {
                    continue;
                }
                Enumeration<InetAddress> inetAddresses = networkInterface.getInetAddresses();
                while (inetAddresses.hasMoreElements()) {
                    InetAddress inetAddress = inetAddresses.nextElement();
                    String hostAddress = inetAddress.getHostAddress();
                    // 只添加 IPv4 地址
                    if (!hostAddress.contains(":") && !hostAddress.startsWith("127.")) {
                        ipList.add(hostAddress);
                    }
                }
            }
        } catch (Exception e) {
            log.error("获取网络接口信息失败", e);
        }
        return ipList;
    }
}
