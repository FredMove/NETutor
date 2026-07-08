package ru.chima.netutor_service;

import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class KafkaProducerService {
    private final KafkaTemplate<String, QuestionCorrelationDTO> kafkaTemplate;
    private final CorrelationStore correlationStore;
    public KafkaProducerService(KafkaTemplate<String, QuestionCorrelationDTO> kafkaTemplate, CorrelationStore correlationStore){
        this.kafkaTemplate = kafkaTemplate;
        this.correlationStore = correlationStore;
    }

    public String sendMessage(String topic, QuestionDTO message){

        String correlationId = UUID.randomUUID().toString();
        QuestionCorrelationDTO messageWithId = new QuestionCorrelationDTO(message.question(), correlationId);
        correlationStore.putProcess(correlationId);


        kafkaTemplate.send(topic, messageWithId).whenComplete((result, ex) -> { //.whenComplete гарантирует выполнение только после получения брокером сообщения
            if (ex != null) {
                System.out.println("Ошибка отправки: " + ex.getMessage());
            } else {
                System.out.println("Успешно отправлено, offset: " + result.getRecordMetadata().offset());
            }
        });
        System.out.println("Message send");

        return correlationId;
    }
}
