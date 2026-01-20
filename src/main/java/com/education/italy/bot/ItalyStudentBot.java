package com.education.italy.bot;

import com.education.italy.model.Category;
import com.education.italy.model.FaqItem;
import com.education.italy.repository.FaqRepository;
import com.education.italy.service.BotService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.telegram.telegrambots.bots.TelegramLongPollingBot;
import org.telegram.telegrambots.meta.api.methods.send.SendMessage;
import org.telegram.telegrambots.meta.api.objects.Update;
import org.telegram.telegrambots.meta.api.objects.replykeyboard.InlineKeyboardMarkup;
import org.telegram.telegrambots.meta.api.objects.replykeyboard.buttons.InlineKeyboardButton;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Component
public class ItalyStudentBot extends TelegramLongPollingBot {

    @Value("${bot.username}")
    private String botUsername;

    @Value("${bot.token}")
    private String botToken;

    private final BotService botService;
    private final FaqRepository faqRepository;

    // Simple in-memory user language state. In prod, use DB.
    private final Map<Long, String> userLanguages = new HashMap<>();

    public ItalyStudentBot(BotService botService, FaqRepository faqRepository) {
        this.botService = botService;
        this.faqRepository = faqRepository;
    }

    @Override
    public String getBotUsername() {
        return botUsername;
    }

    @Override
    public String getBotToken() {
        return botToken;
    }

    @Override
    public void onUpdateReceived(Update update) {
        if (update.hasMessage() && update.getMessage().hasText()) {
            handleMessage(update);
        } else if (update.hasCallbackQuery()) {
            handleCallback(update);
        }
    }

    private void handleMessage(Update update) {
        long chatId = update.getMessage().getChatId();
        String text = update.getMessage().getText();

        if (text.equals("/start")) {
            sendLanguageSelection(chatId);
            return;
        }

        String lang = userLanguages.getOrDefault(chatId, "ru"); // Default RU

        // Search logic
        List<FaqItem> results = botService.search(text, lang);
        if (results.isEmpty()) {
            sendMessage(chatId, lang.equals("ru")
                    ? "Пожалуйста, уточните вопрос или выберите тему из меню."
                    : "Please clarify your question or select a topic from the menu.", true);
        } else if (results.size() == 1) {
            sendAnswer(chatId, results.get(0), lang);
        } else {
            // Multiple results, show suggestions
            sendSuggestions(chatId, results, lang);
        }
    }

    private void handleCallback(Update update) {
        long chatId = update.getCallbackQuery().getMessage().getChatId();
        String data = update.getCallbackQuery().getData();

        if (data.startsWith("LANG_")) {
            String lang = data.split("_")[1].toLowerCase();
            userLanguages.put(chatId, lang);
            sendMainMenu(chatId, lang);
        } else if (data.equals("MENU")) {
            sendMainMenu(chatId, userLanguages.getOrDefault(chatId, "ru"));
        } else if (data.equals("TOPICS")) {
            sendTopics(chatId, userLanguages.getOrDefault(chatId, "ru"));
        } else if (data.startsWith("CAT_")) {
            String catName = data.split("_")[1];
            Category cat = Category.valueOf(catName);
            showCategoryQuestions(chatId, cat, userLanguages.getOrDefault(chatId, "ru"));
        } else if (data.startsWith("FAQ_")) {
            String id = data.split("_")[1];
            faqRepository.findById(id)
                    .ifPresent(item -> sendAnswer(chatId, item, userLanguages.getOrDefault(chatId, "ru")));
        }
    }

    private void sendLanguageSelection(long chatId) {
        SendMessage message = new SendMessage();
        message.setChatId(String.valueOf(chatId));
        message.setText("Benvenuto! Please select your language / Выберите язык:");

        InlineKeyboardMarkup markup = new InlineKeyboardMarkup();
        List<List<InlineKeyboardButton>> rows = new ArrayList<>();
        List<InlineKeyboardButton> row = new ArrayList<>();

        var ruBtn = new InlineKeyboardButton();
        ruBtn.setText("🇷🇺 Русский");
        ruBtn.setCallbackData("LANG_RU");

        var enBtn = new InlineKeyboardButton();
        enBtn.setText("🇬🇧 English");
        enBtn.setCallbackData("LANG_EN");

        row.add(ruBtn);
        row.add(enBtn);
        rows.add(row);
        markup.setKeyboard(rows);
        message.setReplyMarkup(markup);

        try {
            execute(message);
        } catch (TelegramApiException e) {
            e.printStackTrace();
        }
    }

    private void sendMainMenu(long chatId, String lang) {
        SendMessage message = new SendMessage();
        message.setChatId(String.valueOf(chatId));
        message.setText(lang.equals("ru") ? "Главное меню:" : "Main Menu:");

        InlineKeyboardMarkup markup = new InlineKeyboardMarkup();
        List<List<InlineKeyboardButton>> rows = new ArrayList<>();

        // Button: Topics
        var topicsBtn = new InlineKeyboardButton();
        topicsBtn.setText(lang.equals("ru") ? "📚 Темы" : "📚 Topics");
        topicsBtn.setCallbackData("TOPICS");

        // Button: Ask Question (Instruction)
        var askBtn = new InlineKeyboardButton();
        askBtn.setText(lang.equals("ru") ? "❓ Задать вопрос" : "❓ Ask Question");
        // For simplicity, just tells user to type
        askBtn.setCallbackData("ASK_INSTRUCTION");

        List<InlineKeyboardButton> row1 = new ArrayList<>();
        row1.add(topicsBtn);
        row1.add(askBtn);
        rows.add(row1);

        markup.setKeyboard(rows);
        message.setReplyMarkup(markup);

        try {
            execute(message);
        } catch (TelegramApiException e) {
            e.printStackTrace();
        }
    }

    private void sendTopics(long chatId, String lang) {
        SendMessage message = new SendMessage();
        message.setChatId(String.valueOf(chatId));
        message.setText(lang.equals("ru") ? "Выберите тему:" : "Select a topic:");

        InlineKeyboardMarkup markup = new InlineKeyboardMarkup();
        List<List<InlineKeyboardButton>> rows = new ArrayList<>();

        for (Category cat : Category.values()) {
            List<InlineKeyboardButton> row = new ArrayList<>();
            InlineKeyboardButton btn = new InlineKeyboardButton();
            btn.setText(cat.name()); // Customize display name if needed
            btn.setCallbackData("CAT_" + cat.name());
            row.add(btn);
            rows.add(row);
        }

        var backBtn = new InlineKeyboardButton();
        backBtn.setText(lang.equals("ru") ? "🔙 Назад" : "🔙 Back");
        backBtn.setCallbackData("MENU");
        rows.add(List.of(backBtn));

        markup.setKeyboard(rows);
        message.setReplyMarkup(markup);

        try {
            execute(message);
        } catch (TelegramApiException e) {
            e.printStackTrace();
        }
    }

    private void showCategoryQuestions(long chatId, Category category, String lang) {
        List<FaqItem> items = faqRepository.findByCategoryAndLang(category, lang);

        if (items.isEmpty()) {
            sendMessage(chatId, lang.equals("ru") ? "Нет вопросов в этой категории." : "No questions in this category.",
                    false);
            return;
        }

        SendMessage message = new SendMessage();
        message.setChatId(String.valueOf(chatId));
        message.setText(lang.equals("ru") ? "Вопросы по теме " + category.name() : "Questions on " + category.name());

        InlineKeyboardMarkup markup = new InlineKeyboardMarkup();
        List<List<InlineKeyboardButton>> rows = new ArrayList<>();

        for (FaqItem item : items) {
            List<InlineKeyboardButton> row = new ArrayList<>();
            InlineKeyboardButton btn = new InlineKeyboardButton();
            String qText = item.getQuestion();
            if (qText != null && qText.length() > 30)
                qText = qText.substring(0, 30) + "...";
            btn.setText(qText);
            btn.setCallbackData("FAQ_" + item.getId());
            row.add(btn);
            rows.add(row);
        }

        var backBtn = new InlineKeyboardButton();
        backBtn.setText(lang.equals("ru") ? "🔙 Назад" : "🔙 Back");
        backBtn.setCallbackData("TOPICS");
        rows.add(List.of(backBtn));

        markup.setKeyboard(rows);
        message.setReplyMarkup(markup);

        try {
            execute(message);
        } catch (TelegramApiException e) {
            e.printStackTrace();
        }
    }

    private void sendSuggestions(long chatId, List<FaqItem> results, String lang) {
        SendMessage message = new SendMessage();
        message.setChatId(String.valueOf(chatId));
        message.setText(lang.equals("ru") ? "Возможно, вы имели в виду:" : "Maybe you meant:");

        InlineKeyboardMarkup markup = new InlineKeyboardMarkup();
        List<List<InlineKeyboardButton>> rows = new ArrayList<>();

        for (FaqItem item : results) {
            List<InlineKeyboardButton> row = new ArrayList<>();
            InlineKeyboardButton btn = new InlineKeyboardButton();
            String qText = item.getQuestion();
            btn.setText(qText);
            btn.setCallbackData("FAQ_" + item.getId());
            row.add(btn);
            rows.add(row);
        }

        markup.setKeyboard(rows);
        message.setReplyMarkup(markup);

        try {
            execute(message);
        } catch (TelegramApiException e) {
            e.printStackTrace();
        }
    }

    private void sendAnswer(long chatId, FaqItem item, String lang) {
        String answerText = item.getAnswer();
        SendMessage message = new SendMessage();
        message.setChatId(String.valueOf(chatId));
        message.setText(answerText);

        InlineKeyboardMarkup markup = new InlineKeyboardMarkup();
        List<List<InlineKeyboardButton>> rows = new ArrayList<>();

        var backBtn = new InlineKeyboardButton();
        backBtn.setText(lang.equals("ru") ? "🔙 Вернуться в меню" : "🔙 Back to Menu");
        backBtn.setCallbackData("MENU");
        rows.add(List.of(backBtn));

        markup.setKeyboard(rows);
        message.setReplyMarkup(markup);

        try {
            execute(message);
        } catch (TelegramApiException e) {
            e.printStackTrace();
        }
    }

    private void sendMessage(long chatId, String text, boolean showMenuBtn) {
        SendMessage message = new SendMessage();
        message.setChatId(String.valueOf(chatId));
        message.setText(text);
        if (showMenuBtn) {
            InlineKeyboardMarkup markup = new InlineKeyboardMarkup();
            var btn = new InlineKeyboardButton();
            btn.setText("Menu");
            btn.setCallbackData("MENU");
            markup.setKeyboard(List.of(List.of(btn)));
            message.setReplyMarkup(markup);
        }
        try {
            execute(message);
        } catch (TelegramApiException e) {
            e.printStackTrace();
        }
    }
}
