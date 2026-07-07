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
    public NetutorController(KafkaProducerService kafkaProducerService){
        this.kafkaProducerService = kafkaProducerService;
    }

//    @PostMapping("/ask")
//    public AnswerDTO ask (@RequestBody QuestionDTO request) {
//        String answer = netutorService.askQuestion(request.question());
//        return new AnswerDTO(answer);
//    }

    @PostMapping("/send")
    public String sendMessageKafka(@RequestParam String topic, @RequestBody QuestionDTO message){
        kafkaProducerService.sendMessage(topic, message);
        return "Сообщение отправлено в Kafka";
    }
}
