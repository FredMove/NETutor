package ru.chima.netutor_service;

import org.springframework.stereotype.Component;

import java.util.concurrent.ConcurrentHashMap;

@Component
public class CorrelationStore {
    private final ConcurrentHashMap<String, String> store = new ConcurrentHashMap<>();

    public void put(String correlationId, String status){
        store.put(correlationId, status);
    }

    public void get(String correlationId){
        store.get(correlationId);
    }
}
