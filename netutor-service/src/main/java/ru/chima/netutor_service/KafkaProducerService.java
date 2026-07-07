package ru.chima.netutor_service;

import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

@Service
public class KafkaProducerService {
    private final KafkaTemplate<String, QuestionDTO> kafkaTemplate;
    public KafkaProducerService(KafkaTemplate<String, QuestionDTO> kafkaTemplate){
        this.kafkaTemplate = kafkaTemplate;
    }

    public void sendMessage(String topic, QuestionDTO message){
        kafkaTemplate.send(topic, message).whenComplete((result, ex) -> {
            if (ex != null) {
                System.out.println("Ошибка отправки: " + ex.getMessage());
            } else {
                System.out.println("Успешно отправлено, offset: " + result.getRecordMetadata().offset());
            }
        });
        System.out.println("Message send");
    }
}
