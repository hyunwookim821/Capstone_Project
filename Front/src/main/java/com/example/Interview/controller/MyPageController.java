package com.example.Interview.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@RequestMapping("myPage")
@Controller
public class MyPageController {

    @GetMapping
    public String myPage() {
        return "/myPage/myPage";
    }
}
