package ru.chima.netutor_service;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/chat")
public class NetutorController {
//    private final NetutorService netutorService;
//
//
//    public NetutorController(NetutorService netutorService){
//        this.netutorService = netutorService;
//    }

    private final KafkaProducerService kafkaProducerService;
    private final CorrelationStore correlationStore;
    public NetutorController(KafkaProducerService kafkaProducerService, CorrelationStore correlationStore){
        this.kafkaProducerService = kafkaProducerService;
        this.correlationStore = correlationStore;
    }

//    @PostMapping("/ask")
//    public AnswerDTO ask (@RequestBody QuestionDTO request) {
//        String answer = netutorService.askQuestion(request.question());
//        return new AnswerDTO(answer);
//    }

    @PostMapping("/send")
    public String sendMessageKafka(@RequestParam String topic, @RequestBody QuestionDTO message){
        return kafkaProducerService.sendMessage(topic, message);
    }

    @GetMapping("/answer/{correlationId}")
    public String getMessageKafka(@PathVariable String correlationId){
        return correlationStore.get(correlationId);
    }
}
