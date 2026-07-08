package ru.chima.netutor_service;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.core.*;
import org.springframework.kafka.support.serializer.JacksonJsonDeserializer;
import org.springframework.kafka.support.serializer.JacksonJsonSerializer;

import java.util.HashMap;
import java.util.Map;

@Configuration
public class KafkaProducerConfig {
    @Bean
    public ProducerFactory<String, QuestionCorrelationDTO> producerFactory(){
        Map<String, Object> producerConfigProps = new HashMap<>();
        producerConfigProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9094");
        producerConfigProps.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        producerConfigProps.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JacksonJsonSerializer.class);
        return new DefaultKafkaProducerFactory<>(producerConfigProps);
    }

    @Bean
    public KafkaTemplate<String, QuestionCorrelationDTO> kafkaTemplate() {
        return new KafkaTemplate<>(producerFactory()); //Просто шаблон для отправки продюсером сообщения
    }

    @Bean
    public ConsumerFactory<String, AnswerDTO> consumerFactory(){
        Map<String, Object> consumerConfigProps = new HashMap<>();
        consumerConfigProps.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9094");
        consumerConfigProps.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        consumerConfigProps.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, JacksonJsonDeserializer.class);
        consumerConfigProps.put(JacksonJsonDeserializer.TRUSTED_PACKAGES, "*"); //У Jackson по умолчанию стоит бан на все неизвестные пакеты
        consumerConfigProps.put(ConsumerConfig.GROUP_ID_CONFIG, "netutor-message-listeners");
        return new DefaultKafkaConsumerFactory<>(consumerConfigProps, new StringDeserializer(), new JacksonJsonDeserializer<>(AnswerDTO.class) );
    }

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, AnswerDTO> kafkaListenerContainerFactory(ConsumerFactory<String, AnswerDTO> consumerFactory){ // Важно чтобы метод назывался именно kafkaListenerContainerFactory, т.к. спринг для @KafkaListener ищет именно его
        ConcurrentKafkaListenerContainerFactory<String, AnswerDTO> factory = new ConcurrentKafkaListenerContainerFactory<>(); //Мы делаем контейнер, который будет на постоянной основе дергать брокера на предмет новых сообщений. Весь этот метод - основная разница между работой продюсера и консьюмера: если продюсеру просто нужно отправить сообщение при вызове, то консьюмеру нужно постоянно, бесконечно в фоне прослушивать новые сообщения
        factory.setConsumerFactory(consumerFactory);
        return factory;
    }
}
