package ru.chima.netutor_service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class WebClientConfig {
    @Bean
    public WebClient ragWebClient(@Value("${rag.service.url}") String ragServiceUrl){
        return WebClient.builder()
                .baseUrl(ragServiceUrl)
                .build();
    }
}
