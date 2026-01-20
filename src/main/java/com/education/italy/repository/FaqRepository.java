package com.education.italy.repository;

import com.education.italy.model.Category;
import com.education.italy.model.FaqItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface FaqRepository extends JpaRepository<FaqItem, String> {
    List<FaqItem> findByCategoryAndLang(Category category, String lang);

    // Simple database-side search using LIKE
    // For better search, full-text search capability of Postgres (tsvector) could
    // be used, but this is simple start.
    // Search by question OR keywords (case-insensitive) for a specific language
    List<FaqItem> findByLangAndQuestionContainingIgnoreCaseOrLangAndKeywordsContainingIgnoreCase(
            String lang1, String questionPart, String lang2, String keywordsPart);
}
