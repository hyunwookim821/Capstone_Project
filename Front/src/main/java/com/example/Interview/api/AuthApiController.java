package com.example.Interview.api;

import com.example.Interview.dto.LoginRequest;
import com.example.Interview.dto.MemberResponse;
import com.example.Interview.dto.SignupRequest;
import com.example.Interview.service.AuthService;
import jakarta.servlet.http.HttpSession;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthApiController {

    private static final Logger logger = LoggerFactory.getLogger(AuthApiController.class);
    private final AuthService authService;

    public AuthApiController(AuthService authService) {
        this.authService = authService;
    }

    @PostMapping("/signup")
    public ResponseEntity<MemberResponse> signup(@RequestBody SignupRequest req) {
        return ResponseEntity.ok(authService.signup(req));
    }

    @PostMapping("/login")
    public ResponseEntity<Map<String, String>> login(@RequestBody LoginRequest req, HttpSession session) {
        logger.info("Attempting login for email: {}", req.getEmail());
        AuthService.FastAPIAuthToken token = authService.login(req);
        session.setAttribute("token", token.access_token);
        logger.info("Token stored in session for email: {}", req.getEmail());
        return ResponseEntity.ok(Map.of("message", "Login successful"));
    }

    @PostMapping("/logout")
    public ResponseEntity<Map<String, String>> logout(HttpSession session) {
        logger.info("Logging out user by invalidating session.");
        session.invalidate(); // Invalidate the session to remove all attributes, including the token
        return ResponseEntity.ok(Map.of("message", "Logout successful"));
    }

    @ExceptionHandler(ResponseStatusException.class)
    public ResponseEntity<Map<String, String>> handleResponseStatusException(ResponseStatusException ex) {
        logger.warn("Handling ResponseStatusException: {}", ex.getReason());
        return ResponseEntity
                .status(ex.getStatusCode())
                .body(Map.of("message", ex.getReason()));
    }
}
