package skid.vortex.auth;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.concurrent.CompletableFuture;

/**
 * Vortex License Client - Authenticates with Railway-hosted license server
 * Compatible with vortex-license server
 */
public class VortexAuthClient {
    // Set these to your Railway deployment URL
    private static final String AUTH_SERVER_URL = "http://localhost:5000"; // Change to Railway URL
    private static final String VALIDATE_ENDPOINT = "/auth/validate";
    private static final String LICENSE_FILE_PATH = "vortex_license.txt";
    
    private static final HttpClient client = HttpClient.newHttpClient();
    private static String cachedHWID = null;
    private static String cachedLicense = null;
    private static boolean isAuthenticated = false;
    
    /**
     * Generate HWID from system information (SHA256)
     */
    public static String generateHWID() {
        if (cachedHWID != null) {
            return cachedHWID;
        }
        
        try {
            String data = System.getProperty("os.name") +
                    System.getProperty("os.arch") +
                    System.getProperty("os.version") +
                    System.getProperty("user.name");
            
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] hash = md.digest(data.getBytes(StandardCharsets.UTF_8));
            
            StringBuilder hex = new StringBuilder();
            for (byte b : hash) {
                hex.append(String.format("%02x", b));
            }
            
            cachedHWID = hex.toString();
            System.out.println("[Vortex Auth] Generated HWID: " + cachedHWID.substring(0, 8));
            return cachedHWID;
        } catch (Exception e) {
            System.err.println("[Vortex Auth] HWID generation failed: " + e.getMessage());
            cachedHWID = "UNKNOWN";
            return "UNKNOWN";
        }
    }
    
    /**
     * Load license from local cache file
     */
    public static String loadCachedLicense() {
        try {
            if (Files.exists(Paths.get(LICENSE_FILE_PATH))) {
                String license = new String(Files.readAllBytes(Paths.get(LICENSE_FILE_PATH)), 
                        StandardCharsets.UTF_8).trim();
                if (!license.isEmpty()) {
                    cachedLicense = license;
                    System.out.println("[Vortex Auth] License loaded from cache");
                    return license;
                }
            }
        } catch (Exception e) {
            System.err.println("[Vortex Auth] Failed to read license cache: " + e.getMessage());
        }
        return null;
    }
    
    /**
     * Save license to local cache
     */
    private static void saveLicenseCache(String license) {
        try {
            Files.write(Paths.get(LICENSE_FILE_PATH), license.getBytes(StandardCharsets.UTF_8));
            System.out.println("[Vortex Auth] License cached successfully");
        } catch (Exception e) {
            System.err.println("[Vortex Auth] Failed to cache license: " + e.getMessage());
        }
    }
    
    /**
     * Authenticate with server - Compatible with vortex-license server
     * Sends POST request with: hwid, license_key, username
     */
    public static CompletableFuture<Boolean> authenticate(String licenseKey, String username) {
        String hwid = generateHWID();
        
        JsonObject requestBody = new JsonObject();
        requestBody.addProperty("hwid", hwid);
        requestBody.addProperty("license_key", licenseKey);
        requestBody.addProperty("username", username);
        requestBody.addProperty("mode", "login");
        
        String url = AUTH_SERVER_URL + VALIDATE_ENDPOINT;
        System.out.println("[Vortex Auth] Authenticating with: " + url);
        
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(requestBody.toString()))
                .build();
        
        return client.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenApply(response -> {
                    try {
                        if (response.statusCode() != 200) {
                            System.err.println("[Vortex Auth] Server error: " + response.statusCode());
                            return false;
                        }
                        
                        JsonObject jsonResponse = JsonParser.parseString(response.body())
                                .getAsJsonObject();
                        
                        if (jsonResponse.has("valid") && jsonResponse.get("valid").getAsBoolean()) {
                            System.out.println("[Vortex Auth] Authentication successful!");
                            isAuthenticated = true;
                            cachedLicense = licenseKey;
                            saveLicenseCache(licenseKey);
                            return true;
                        } else {
                            System.err.println("[Vortex Auth] Authentication failed: " + 
                                    jsonResponse.get("error").getAsString());
                            return false;
                        }
                    } catch (Exception e) {
                        System.err.println("[Vortex Auth] Authentication exception: " + e.getMessage());
                        return false;
                    }
                });
    }
    
    /**
     * Quick login with cached license (offline mode)
     */
    public static CompletableFuture<Boolean> quickLogin(String username) {
        String cachedLic = loadCachedLicense();
        if (cachedLic != null) {
            return authenticate(cachedLic, username);
        }
        return CompletableFuture.completedFuture(false);
    }
    
    /**
     * Register new license (user provides key from server)
     */
    public static CompletableFuture<Boolean> registerLicense(String licenseKey, String username) {
        return authenticate(licenseKey, username);
    }
    
    public static boolean isAuthenticated() {
        return isAuthenticated;
    }
    
    public static void setAuthenticated(boolean auth) {
        isAuthenticated = auth;
    }
    
    public static String getHWID() {
        return generateHWID();
    }
}
