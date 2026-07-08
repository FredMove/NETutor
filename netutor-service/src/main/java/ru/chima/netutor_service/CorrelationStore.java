package ru.chima.netutor_service;

import org.springframework.stereotype.Component;

import java.util.concurrent.ConcurrentHashMap;

@Component
public class CorrelationStore {
    private final ConcurrentHashMap<String, String> store = new ConcurrentHashMap<>();

    public void putProcess(String correlationId){
        store.put(correlationId, "");
    }

    public void putAnswer(String correlationId, String answer){
        store.put(correlationId, answer);
    }

    public String get(String correlationId){
        return store.get(correlationId);
    }
}
