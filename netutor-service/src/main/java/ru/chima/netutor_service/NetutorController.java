package ru.chima.netutor_service;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/chat")
public class NetutorController {
    private final NetutorService netutorService;

    public NetutorController(NetutorService netutorService){
        this.netutorService = netutorService;
    }

    @PostMapping("/ask")
    public AnswerDTO ask (@RequestBody QuestionDTO request) {
        String answer = netutorService.askQuestion(request.question());
        return new AnswerDTO(answer);
    }
}
