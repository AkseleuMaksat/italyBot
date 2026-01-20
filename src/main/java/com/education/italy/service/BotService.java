package com.education.italy.service;

import com.education.italy.model.Category;
import com.education.italy.model.FaqItem;
import com.education.italy.repository.FaqRepository;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PostConstruct;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
public class BotService {

    private final FaqRepository faqRepository;
    private final ObjectMapper objectMapper;

    public BotService(FaqRepository faqRepository, ObjectMapper objectMapper) {
        this.faqRepository = faqRepository;
        this.objectMapper = objectMapper;
    }

    @PostConstruct
    public void initDb() {
        if (faqRepository.count() == 0) {
            System.out.println("DB is empty. Loading initial data from JSON...");
            try {
                ClassPathResource resource = new ClassPathResource("faq.json");
                // The JSON structure in faq.json was:
                // [ { "id": "1", "category": "ADMISSION", "question": {"ru": "...", "en":
                // "..."}, "answer": {...}, "keywords": [...] } ]
                // We need to map this to the NEW FaqItem entity structure:
                // One FaqItem per language per question.

                // Let's read it as a generic list of maps first to manually map it
                List<Map<String, Object>> rawItems = objectMapper.readValue(resource.getInputStream(),
                        new TypeReference<>() {
                        });

                List<FaqItem> entities = new ArrayList<>();

                for (Map<String, Object> raw : rawItems) {
                    // String originalId = (String) raw.get("id"); // Not used as PK anymore,
                    // generating UUIDs or using it as prefix
                    String distinctId = UUID.randomUUID().toString(); // Use random for grouping or just independent
                                                                      // items?
                    // The user requirement said: "One record = one language".
                    // So for 1 JSON item with RU and EN, we create 2 Entities.

                    Category category = Category.valueOf(((String) raw.get("category")));
                    Map<String, String> questions = objectMapper.convertValue(raw.get("question"),
                            new TypeReference<>() {
                            });
                    Map<String, String> answers = objectMapper.convertValue(raw.get("answer"), new TypeReference<>() {
                    });
                    List<String> keywordsList = objectMapper.convertValue(raw.get("keywords"), new TypeReference<>() {
                    });
                    String keywords = keywordsList != null ? String.join(",", keywordsList) : "";

                    // RU
                    if (questions.containsKey("ru") && answers.containsKey("ru")) {
                        entities.add(new FaqItem(
                                UUID.randomUUID().toString(),
                                category,
                                "ru",
                                questions.get("ru"),
                                answers.get("ru"),
                                keywords));
                    }

                    // EN
                    if (questions.containsKey("en") && answers.containsKey("en")) {
                        entities.add(new FaqItem(
                                UUID.randomUUID().toString(),
                                category,
                                "en",
                                questions.get("en"),
                                answers.get("en"),
                                keywords));
                    }
                }

                faqRepository.saveAll(entities);
                System.out.println("Loaded " + entities.size() + " items into DB.");

            } catch (IOException e) {
                System.err.println("Failed to load initial data: " + e.getMessage());
            }
        }
    }

    public List<FaqItem> search(String query, String lang) {
        String lowerQuery = query.toLowerCase();

        // 1. Try finding by keyword (simple fuzzy simulation via LIKE)
        // 1. Try finding by keyword (simple fuzzy simulation via LIKE)
        // We search if question contains query OR keywords contains query, AND lang
        // matches
        List<FaqItem> results = faqRepository
                .findByLangAndQuestionContainingIgnoreCaseOrLangAndKeywordsContainingIgnoreCase(
                        lang, lowerQuery, lang, lowerQuery);

        // If results are empty, we might want to search in Category names or Keywords
        // too.
        if (results.isEmpty()) {
            // Fallback: This is where more complex logic fits.
            // For now, let's just return empty or maybe exact match?
        }

        return results;
    }
}
