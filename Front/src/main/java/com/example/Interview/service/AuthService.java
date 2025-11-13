package com.example.Interview.service;

import com.example.Interview.dto.LoginRequest;
import com.example.Interview.dto.MemberResponse;
import com.example.Interview.dto.SignupRequest;
import com.example.Interview.entity.Member;
import com.example.Interview.repository.MemberRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder; // Keep for now, might be removed later
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.server.ResponseStatusException;
import reactor.core.publisher.Mono;

import java.util.Map;

@Service
@Transactional
public class AuthService {

    private final WebClient webClient;

    public AuthService(WebClient webClient) {
        this.webClient = webClient;
    }

    // DTOs for FastAPI communication
    private static class FastAPIUserCreate {
        public String email;
        public String password;
        public String user_name; // Changed from full_name
    }

    private static class FastAPIUserResponse {
        public int user_id;
        public String email;
        public String user_name; // Changed from full_name
        // Add other fields if FastAPI user response has them
    }

    private static class FastAPIAuthToken {
        public String access_token;
        public String token_type;
    }

    public MemberResponse signup(SignupRequest req) {
        if (!req.isTerms()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "이용약관에 동의해야 합니다.");
        }
        if (req.getPassword() == null || !req.getPassword().equals(req.getConfirmPassword())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "비밀번호가 일치하지 않습니다.");
        }

        String email = req.getEmail() == null ? null : req.getEmail().toLowerCase();

        // Call FastAPI /api/v1/users/ for signup
        FastAPIUserCreate fastapiUserCreate = new FastAPIUserCreate();
        fastapiUserCreate.email = email;
        fastapiUserCreate.password = req.getPassword();
        fastapiUserCreate.user_name = req.getNickname(); // Map nickname to user_name

        try {
            FastAPIUserResponse fastapiUserResponse = webClient.post()
                    .uri("/users/")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(Mono.just(fastapiUserCreate), FastAPIUserCreate.class)
                    .retrieve()
                    .onStatus(HttpStatus.CONFLICT::equals, clientResponse ->
                            Mono.error(new ResponseStatusException(HttpStatus.CONFLICT, "이미 사용 중인 이메일입니다.")))
                    .onStatus(status -> status.value() == 422, clientResponse ->
                            clientResponse.bodyToMono(String.class).flatMap(errorBody ->
                                    Mono.error(new ResponseStatusException(HttpStatus.UNPROCESSABLE_ENTITY, "요청 데이터가 올바르지 않습니다: " + errorBody))))
                    .onStatus(status -> status.isError(), clientResponse ->
                            clientResponse.bodyToMono(String.class).flatMap(errorBody ->
                                    Mono.error(new ResponseStatusException(clientResponse.statusCode(), "FastAPI 회원가입 오류: " + errorBody))))
                    .bodyToMono(FastAPIUserResponse.class)
                    .block(); // Blocking call for simplicity

            // Convert FastAPI response to MemberResponse
            Member member = new Member(); // Create a dummy Member or fetch from local DB if needed
            member.setEmail(fastapiUserResponse.email);
            member.setNickname(fastapiUserResponse.user_name); // Map user_name to nickname
            // Note: passwordHash is not set here as FastAPI handles it
            return MemberResponse.from(member);

        } catch (ResponseStatusException e) {
            throw e;
        } catch (Exception e) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "FastAPI 회원가입 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Transactional(readOnly = true)
    public MemberResponse login(LoginRequest req) {
        String email = req.getEmail() == null ? null : req.getEmail().toLowerCase();

        // Call FastAPI /api/v1/login/token for login
        try {
            FastAPIAuthToken authToken = webClient.post()
                    .uri("/login/token")
                    .contentType(MediaType.APPLICATION_FORM_URLENCODED)
                    .body(BodyInserters.fromFormData("username", email).with("password", req.getPassword()))
                    .retrieve()
                    .onStatus(HttpStatus.UNAUTHORIZED::equals, clientResponse ->
                            Mono.error(new ResponseStatusException(HttpStatus.UNAUTHORIZED, "이메일 또는 비밀번호가 일치하지 않습니다.")))
                    .onStatus(status -> status.isError(), clientResponse ->
                            clientResponse.bodyToMono(String.class).flatMap(errorBody ->
                                    Mono.error(new ResponseStatusException(clientResponse.statusCode(), "FastAPI 로그인 오류: " + errorBody))))
                    .bodyToMono(FastAPIAuthToken.class)
                    .block(); // Blocking call for simplicity

            // Here you would typically store the authToken.access_token in a session
            // or return it to the client. For now, we'll create a dummy MemberResponse.
            Member member = new Member();
            member.setEmail(email);
            // In a real app, you might call another FastAPI endpoint to get user details
            // using the token, or FastAPI's login response might include more user info.
            return MemberResponse.from(member);

        } catch (ResponseStatusException e) {
            throw e;
        } catch (Exception e) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "FastAPI 로그인 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Transactional(readOnly = true)
    public MemberResponse findByEmail(String emailRaw) {
        // This method is no longer supported as user management is delegated to FastAPI.
        throw new UnsupportedOperationException("Finding user by email is not supported in this service anymore.");
    }
}
