package ru.chima.netutor_service;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

@Service
public class KafkaConsumerService {
    @KafkaListener(topics = "answers")
    public void listen(String message){
        System.out.println("Получено сообщение: " + message);
    }
}
