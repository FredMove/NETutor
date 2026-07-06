package ru.chima.netutor_service;

import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

@Service
public class NetutorService {
    private final WebClient webClient;
    public NetutorService(WebClient ragWebClient){
        this.webClient = ragWebClient;
    }

    public String askQuestion(String question){
        QuestionDTO request = new QuestionDTO(question);
        AnswerDTO response = webClient.post()
                .uri("/ask")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(AnswerDTO.class)
                .block();

        return response.answer();
    }
}
