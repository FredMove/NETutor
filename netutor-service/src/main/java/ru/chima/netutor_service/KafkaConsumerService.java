package ru.chima.netutor_service;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

@Service
public class KafkaConsumerService {
    private final CorrelationStore correlationStore;

    public KafkaConsumerService(CorrelationStore correlationStore){
        this.correlationStore = correlationStore;
    }
    @KafkaListener(topics = "answers")
    public void listen(AnswerDTO answer){
        String correlationId = answer.correlationId();
        String answerMessage = answer.answer();
        correlationStore.putAnswer(correlationId, answerMessage);

        System.out.println("Получено сообщение: " + answerMessage);
    }
}
