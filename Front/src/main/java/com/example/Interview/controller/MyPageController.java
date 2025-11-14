package com.example.Interview.controller;

import com.example.Interview.dto.UserDto;
import com.example.Interview.service.UserService;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.http.HttpStatus;

@RequestMapping("myPage")
@Controller
@RequiredArgsConstructor
public class MyPageController {

    private final UserService userService;
    private final ObjectMapper objectMapper; // Inject ObjectMapper

    @GetMapping
    public String myPage(HttpSession session, Model model) {
        String token = (String) session.getAttribute("token");
        System.out.println("MyPageController - Session Token: " + token); // Logging: Token

        if (token == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "로그인이 필요합니다.");
        }

        try {
            UserDto userProfile = userService.getUserProfile(token).block();
            System.out.println("MyPageController - Fetched UserProfile DTO: " + userProfile); // Logging: UserDto

            // Serialize user profile to JSON string to safely pass it to the template
            String userJson = objectMapper.writeValueAsString(userProfile);
            System.out.println("MyPageController - Serialized userJson: " + userJson); // Logging: JSON String

            model.addAttribute("userJson", userJson);
            model.addAttribute("token", token);
        } catch (JsonProcessingException e) {
            System.err.println("Error serializing user profile: " + e.getMessage());
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "사용자 정보를 처리하는데 실패했습니다.", e);
        } catch (Exception e) {
            System.err.println("Error fetching user profile for myPage: " + e.getMessage());
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "사용자 정보를 불러오는데 실패했습니다.", e);
        }

        return "/myPage/myPage";
    }
}
