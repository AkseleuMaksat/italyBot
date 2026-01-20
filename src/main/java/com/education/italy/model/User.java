package com.education.italy.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.LocalDateTime;

@Entity
@Table(name = "users")
public class User {

    @Id
    private Long chatId;

    @Column(nullable = false, length = 10)
    private String language; // "ru" or "en"

    private LocalDateTime registeredAt;

    public User() {
    }

    public User(Long chatId, String language, LocalDateTime registeredAt) {
        this.chatId = chatId;
        this.language = language;
        this.registeredAt = registeredAt;
    }

    public Long getChatId() {
        return chatId;
    }

    public void setChatId(Long chatId) {
        this.chatId = chatId;
    }

    public String getLanguage() {
        return language;
    }

    public void setLanguage(String language) {
        this.language = language;
    }

    public LocalDateTime getRegisteredAt() {
        return registeredAt;
    }

    public void setRegisteredAt(LocalDateTime registeredAt) {
        this.registeredAt = registeredAt;
    }
}
