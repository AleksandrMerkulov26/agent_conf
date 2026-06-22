class AmbiguityHandler:
    def handle_multiple_candidates(self, candidates, user_input):
        """
        Если нашлось несколько возможных владельцев, 
        агент задает уточняющие вопросы
        """
        if len(candidates) == 1:
            return candidates[0]
        
        print("🤔 Найдено несколько возможных владельцев:")
        for i, candidate in enumerate(candidates, 1):
            print(f"{i}. {candidate['team']} - {candidate['description']}")
        
        # Просим пользователя выбрать
        choice = input("Выберите номер (1-{len(candidates)}): ")
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(candidates):
                return candidates[idx]
        except:
            pass
        
        # Если пользователь не выбрал, пробуем по-умному:
        # Сравниваем с историей запросов этого пользователя
        # Или используем нейросеть, чтобы выбрать наиболее вероятный вариант
        
        return self._smart_select(candidates, user_input)
    
    def _smart_select(self, candidates, user_input):
        """Используем эвристики для выбора"""
        # Например: если в запросе есть слово "payment", выбираем команду с этим словом в названии
        for candidate in candidates:
            if any(word in candidate['team'].lower() for word in user_input.lower().split()):
                return candidate
        
        # Или выбираем ту, у которой выше "рейтинг" (если он есть)
        return max(candidates, key=lambda x: x.get('confidence', 0))
