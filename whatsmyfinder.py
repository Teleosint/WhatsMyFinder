#!/usr/bin/env python3
"""
WhatsMyFinder - OSINT Username Search Tool
Version: 2.0.0
Author: @Osinter_Telegram
Database Source: WebBreacher/WhatsMyName
"""

import json
import asyncio
import aiohttp
import ssl
import os
import sys
import csv
import uuid
from datetime import datetime
from typing import Dict, List, Set, Optional
from urllib.parse import urlparse
import colorama
from colorama import Fore, Style, Back

# Инициализация colorama
colorama.init()

class WhatsMyFinder:
    """Основной класс приложения"""
    
    def __init__(self):
        self.config = self.load_config()
        self.locale = self.load_locale()
        self.database = None
        self.selected_categories = set()
        self.export_format = "html"
        self.language = self.config["ui"]["default_language"]
        
        # Создаем необходимые папки
        self.create_directories()
        
    def load_config(self) -> Dict:
        """Загружает конфигурацию"""
        config_path = "config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"{Fore.RED}❌ Ошибка загрузки config.json: {e}{Style.RESET_ALL}")
        
        # Конфигурация по умолчанию
        return {
            "app": {
                "name": "WhatsMyFinder",
                "version": "2.0.0",
                "author": "@Osinter_Telegram",
                "data_source": "WebBreacher/WhatsMyName"
            },
            "paths": {
                "database": "wmn-data.json",
                "reports_html": "reports/html",
                "reports_csv": "reports/csv",
                "locales": "locales"
            },
            "search": {
                "default_concurrent_requests": 5,
                "default_timeout": 15,
                "max_sites_per_category": 100
            },
            "ui": {
                "default_language": "ru",
                "available_languages": ["ru", "en"],
                "colors_enabled": True
            }
        }
    
    def load_locale(self) -> Dict:
        """Загружает локализацию"""
        lang = self.config["ui"]["default_language"]
        locale_path = f"{self.config['paths']['locales']}/{lang}.json"
        
        if os.path.exists(locale_path):
            try:
                with open(locale_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"{Fore.RED}❌ Ошибка загрузки локализации: {e}{Style.RESET_ALL}")
        
        # Локализация по умолчанию (английская)
        return {
            "app": {"name": "WhatsMyFinder"},
            "menu": {"title": "WhatsMyFinder"},
            "errors": {"no_database": "Database not found"}
        }
    
    def change_language(self, lang: str):
        """Изменяет язык интерфейса"""
        if lang in self.config["ui"]["available_languages"]:
            self.language = lang
            self.locale = self.load_locale()
            self.save_config()
    
    def save_config(self):
        """Сохраняет конфигурацию"""
        try:
            self.config["ui"]["default_language"] = self.language
            with open("config.json", 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Не удалось сохранить настройки: {e}{Style.RESET_ALL}")
    
    def create_directories(self):
        """Создает необходимые директории"""
        os.makedirs(self.config["paths"]["reports_html"], exist_ok=True)
        os.makedirs(self.config["paths"]["reports_csv"], exist_ok=True)
        os.makedirs(self.config["paths"]["locales"], exist_ok=True)
    
    def load_database(self) -> bool:
        """Загружает базу данных"""
        db_path = self.config["paths"]["database"]
        
        if not os.path.exists(db_path):
            print(f"\n{Fore.RED}{self.locale['errors']['no_database']}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{self.locale['errors']['download_db'].format(self.config['app']['data_source_url'])}{Style.RESET_ALL}")
            return False
        
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                self.database = json.load(f)
            
            print(f"{Fore.GREEN}✅ База данных загружена:{Style.RESET_ALL}")
            print(f"  📊 Сайтов: {len(self.database.get('sites', []))}")
            print(f"  📂 Категорий: {len(self.database.get('categories', []))}")
            print(f"  📍 Источник: {self.config['app']['data_source']}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Ошибка загрузки базы данных: {e}{Style.RESET_ALL}")
            return False
    
    def clear_screen(self):
        """Очищает экран терминала"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Выводит заголовок приложения"""
        self.clear_screen()
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🔍 {self.locale['app']['name']} v{self.config['app']['version']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.locale['app']['description']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📍 {self.locale['app']['database_source']}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}👤 Автор: {self.config['app']['author']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    def main_menu(self):
        """Главное меню"""
        while True:
            self.print_header()
            
            print(f"{Fore.YELLOW}📋 {self.locale['menu']['title']}{Style.RESET_ALL}\n")
            print(f"{Fore.GREEN}1.{Style.RESET_ALL} {self.locale['menu']['search_username']}")
            print(f"{Fore.GREEN}2.{Style.RESET_ALL} {self.locale['menu']['select_categories']}")
            print(f"{Fore.GREEN}3.{Style.RESET_ALL} {self.locale['menu']['export_format']}")
            print(f"{Fore.GREEN}4.{Style.RESET_ALL} {self.locale['menu']['settings']}")
            print(f"{Fore.RED}5.{Style.RESET_ALL} {self.locale['menu']['exit']}")
            
            choice = input(f"\n{Fore.CYAN}➜ Выберите действие (1-5): {Style.RESET_ALL}").strip()
            
            if choice == "1":
                self.search_username_menu()
            elif choice == "2":
                self.select_categories_menu()
            elif choice == "3":
                self.select_export_format_menu()
            elif choice == "4":
                self.settings_menu()
            elif choice == "5":
                print(f"\n{Fore.GREEN}👋 {self.locale['menu']['exit']}{Style.RESET_ALL}")
                sys.exit(0)
            else:
                print(f"{Fore.RED}❌ Неверный выбор{Style.RESET_ALL}")
    
    def search_username_menu(self):
        """Меню поиска username"""
        self.print_header()
        
        if not self.database and not self.load_database():
            input(f"\n{Fore.YELLOW}⏎ Нажмите Enter для возврата...{Style.RESET_ALL}")
            return
        
        print(f"{Fore.YELLOW}🔍 {self.locale['search']['enter_username']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*40}{Style.RESET_ALL}")
        
        username = input(f"\n{Fore.GREEN}➜ Username: {Style.RESET_ALL}").strip()
        
        if not username:
            return
        
        # Показываем выбранные настройки
        print(f"\n{Fore.CYAN}⚙️  Текущие настройки:{Style.RESET_ALL}")
        print(f"  📂 Категории: {len(self.selected_categories) if self.selected_categories else 'Все'}")
        print(f"  📄 Формат: {self.export_format.upper()}")
        
        confirm = input(f"\n{Fore.YELLOW}▶️  Начать поиск? (y/n): {Style.RESET_ALL}").strip().lower()
        
        if confirm == 'y':
            asyncio.run(self.perform_search(username))
        
        input(f"\n{Fore.YELLOW}⏎ Нажмите Enter для возврата...{Style.RESET_ALL}")
    
    def select_categories_menu(self):
        """Меню выбора категорий"""
        if not self.database and not self.load_database():
            input(f"\n{Fore.YELLOW}⏎ Нажмите Enter для возврата...{Style.RESET_ALL}")
            return
        
        while True:
            self.print_header()
            print(f"{Fore.YELLOW}📂 {self.locale['categories']['title']}{Style.RESET_ALL}\n")
            
            categories = self.database.get("categories", [])
            
            # Выводим категории с номерами
            for i, category in enumerate(sorted(categories), 1):
                marker = "✅ " if category in self.selected_categories else "  "
                print(f"{Fore.GREEN}{i:2d}.{Style.RESET_ALL} {marker}{category}")
            
            print(f"\n{Fore.CYAN}{'─'*40}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{self.locale['categories']['selected_count'].format(len(self.selected_categories))}{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Команды:{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}all{Style.RESET_ALL} - {self.locale['categories']['select_all']}")
            print(f"  {Fore.RED}none{Style.RESET_ALL} - {self.locale['categories']['deselect_all']}")
            print(f"  {Fore.YELLOW}done{Style.RESET_ALL} - {self.locale['categories']['confirm']}")
            print(f"  {Fore.RED}back{Style.RESET_ALL} - {self.locale['menu']['back']}")
            
            choice = input(f"\n{Fore.CYAN}➜ Выберите категории (номера/команды): {Style.RESET_ALL}").strip().lower()
            
            if choice == 'all':
                self.selected_categories = set(categories)
            elif choice == 'none':
                self.selected_categories = set()
            elif choice == 'done':
                break
            elif choice == 'back':
                return
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(categories):
                    category = sorted(categories)[idx]
                    if category in self.selected_categories:
                        self.selected_categories.remove(category)
                    else:
                        self.selected_categories.add(category)
    
    def select_export_format_menu(self):
        """Меню выбора формата экспорта"""
        self.print_header()
        print(f"{Fore.YELLOW}📄 {self.locale['export']['title']}{Style.RESET_ALL}\n")
        
        formats = [
            ("1", "html", self.locale['export']['html_desc']),
            ("2", "csv", self.locale['export']['csv_desc']),
            ("3", "both", f"{self.locale['export']['html']} + {self.locale['export']['csv']}")
        ]
        
        for num, fmt, desc in formats:
            marker = "✅ " if self.export_format == fmt else "  "
            print(f"{Fore.GREEN}{num}.{Style.RESET_ALL} {marker}{fmt.upper()}: {desc}")
        
        choice = input(f"\n{Fore.CYAN}➜ Выберите формат (1-3): {Style.RESET_ALL}").strip()
        
        if choice in ["1", "2", "3"]:
            self.export_format = formats[int(choice)-1][1]
    
    def settings_menu(self):
        """Меню настроек"""
        while True:
            self.print_header()
            print(f"{Fore.YELLOW}⚙️  {self.locale['settings']['title']}{Style.RESET_ALL}\n")
            
            print(f"{Fore.CYAN}1.{Style.RESET_ALL} {self.locale['settings']['language']}: {self.language.upper()}")
            print(f"{Fore.CYAN}2.{Style.RESET_ALL} {self.locale['settings']['concurrent_requests']}: {self.config['search']['default_concurrent_requests']}")
            print(f"{Fore.CYAN}3.{Style.RESET_ALL} {self.locale['settings']['timeout']}: {self.config['search']['default_timeout']}")
            print(f"{Fore.GREEN}4.{Style.RESET_ALL} {self.locale['settings']['save']}")
            print(f"{Fore.RED}5.{Style.RESET_ALL} {self.locale['menu']['back']}")
            
            choice = input(f"\n{Fore.CYAN}➜ Выберите настройку (1-5): {Style.RESET_ALL}").strip()
            
            if choice == "1":
                self.change_language_setting()
            elif choice == "2":
                self.change_concurrent_requests()
            elif choice == "3":
                self.change_timeout()
            elif choice == "4":
                self.save_config()
                print(f"{Fore.GREEN}✅ Настройки сохранены{Style.RESET_ALL}")
                input(f"\n{Fore.YELLOW}⏎ Нажмите Enter...{Style.RESET_ALL}")
            elif choice == "5":
                return
    
    def change_language_setting(self):
        """Изменение языка"""
        print(f"\n{Fore.YELLOW}🌍 Доступные языки:{Style.RESET_ALL}")
        for lang in self.config["ui"]["available_languages"]:
            print(f"  {Fore.GREEN}{lang.upper()}{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.CYAN}➜ Выберите язык: {Style.RESET_ALL}").strip().lower()
        
        if choice in self.config["ui"]["available_languages"]:
            self.change_language(choice)
            print(f"{Fore.GREEN}✅ Язык изменен на {choice.upper()}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Неверный выбор языка{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}⏎ Нажмите Enter...{Style.RESET_ALL}")
    
    def change_concurrent_requests(self):
        """Изменение количества параллельных запросов"""
        try:
            current = self.config["search"]["default_concurrent_requests"]
            new = input(f"\n{Fore.CYAN}➜ Параллельные запросы (1-10, текущее: {current}): {Style.RESET_ALL}").strip()
            
            if new:
                value = int(new)
                if 1 <= value <= 10:
                    self.config["search"]["default_concurrent_requests"] = value
                    print(f"{Fore.GREEN}✅ Установлено: {value}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Значение должно быть от 1 до 10{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}❌ Введите число{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}⏎ Нажмите Enter...{Style.RESET_ALL}")
    
    def change_timeout(self):
        """Изменение таймаута"""
        try:
            current = self.config["search"]["default_timeout"]
            new = input(f"\n{Fore.CYAN}➜ Таймаут в секундах (5-60, текущее: {current}): {Style.RESET_ALL}").strip()
            
            if new:
                value = int(new)
                if 5 <= value <= 60:
                    self.config["search"]["default_timeout"] = value
                    print(f"{Fore.GREEN}✅ Установлено: {value}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Значение должно быть от 5 до 60{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}❌ Введите число{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}⏎ Нажмите Enter...{Style.RESET_ALL}")
    
    async def check_site(self, session: aiohttp.ClientSession, site_config: Dict, username: str, semaphore: asyncio.Semaphore) -> Dict:
        """Проверяет один сайт"""
        async with semaphore:
            result = {
                "name": site_config.get("name", "Unknown"),
                "url": "",
                "found": False,
                "error": None,
                "category": site_config.get("cat", "unknown"),
                "status": None
            }
            
            try:
                # Подготавливаем URL
                uri_check = site_config.get("uri_check", "")
                if not uri_check or "{account}" not in uri_check:
                    return result
                
                url = uri_check.replace("{account}", username)
                result["url"] = url
                
                # Заголовки
                headers = site_config.get("headers", {})
                if not headers:
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Accept": "text/html",
                    }
                
                # Таймаут из настроек
                timeout = aiohttp.ClientTimeout(total=self.config["search"]["default_timeout"])
                
                # Выполняем запрос
                if site_config.get("post_body"):
                    post_body = site_config.get("post_body", "").replace("{account}", username)
                    async with session.post(url, data=post_body, headers=headers, timeout=timeout, ssl=False) as response:
                        content = await response.text()
                        status = response.status
                else:
                    async with session.get(url, headers=headers, timeout=timeout, ssl=False) as response:
                        content = await response.text()
                        status = response.status
                
                result["status"] = status
                
                # Логика проверки
                expected_code = site_config.get("e_code")
                expected_string = site_config.get("e_string", "")
                missing_code = site_config.get("m_code")
                missing_string = site_config.get("m_string", "")
                
                # Проверяем по правилам
                if expected_code is not None and status == expected_code:
                    if expected_string:
                        result["found"] = expected_string in content
                    else:
                        result["found"] = True
                elif missing_code is not None and status == missing_code:
                    result["found"] = False
                elif missing_string and missing_string in content:
                    result["found"] = False
                else:
                    # Fallback
                    result["found"] = status not in [404, 410, 403, 400]
                    
            except asyncio.TimeoutError:
                result["error"] = "Timeout"
            except Exception as e:
                result["error"] = str(e)[:50]
            
            return result
    
    async def perform_search(self, username: str):
        """Выполняет поиск username"""
        print(f"\n{Fore.YELLOW}{self.locale['search']['searching'].format(username)}{Style.RESET_ALL}")
        
        # Фильтруем сайты по выбранным категориям
        sites = self.database.get("sites", [])
        
        if self.selected_categories:
            filtered_sites = [site for site in sites if site.get("cat") in self.selected_categories]
        else:
            filtered_sites = sites
        
        # Ограничиваем количество сайтов
        max_sites = self.config["search"]["max_sites_per_category"]
        if len(filtered_sites) > max_sites:
            test_sites = filtered_sites[:max_sites]
            print(f"{Fore.YELLOW}⚠️  Ограничение: проверяю первые {max_sites} сайтов{Style.RESET_ALL}")
        else:
            test_sites = filtered_sites
        
        print(f"{Fore.CYAN}{self.locale['search']['checking_sites'].format(len(test_sites))}{Style.RESET_ALL}")
        
        estimated_time = len(test_sites) * 2 / self.config["search"]["default_concurrent_requests"]
        print(f"{Fore.CYAN}{self.locale['search']['time_estimate'].format(int(estimated_time))}{Style.RESET_ALL}")
        
        # Семафор для ограничения запросов
        semaphore = asyncio.Semaphore(self.config["search"]["default_concurrent_requests"])
        
        # Создаем сессию
        connector = aiohttp.TCPConnector(limit=self.config["search"]["default_concurrent_requests"])
        timeout = aiohttp.ClientTimeout(total=30)
        
        results = []
        
        # Прогресс-бар
        total = len(test_sites)
        
        try:
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                # Создаем задачи
                tasks = []
                for i, site in enumerate(test_sites, 1):
                    task = self.check_site(session, site, username, semaphore)
                    tasks.append(task)
                    
                    # Выводим прогресс каждые 10%
                    if i % max(1, total // 10) == 0 or i == total:
                        progress = int((i / total) * 50)
                        bar = "█" * progress + "░" * (50 - progress)
                        percent = int((i / total) * 100)
                        print(f"\r{Fore.GREEN}[{bar}] {percent}% ({i}/{total}){Style.RESET_ALL}", end="", flush=True)
                
                print()  # Новая строка после прогресс-бара
                
                # Выполняем все задачи
                print(f"{Fore.CYAN}⏳ Обработка результатов...{Style.RESET_ALL}")
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
        except Exception as e:
            print(f"{Fore.RED}❌ Ошибка: {e}{Style.RESET_ALL}")
            return
        
        # Обрабатываем результаты
        valid_results = [r for r in results if isinstance(r, dict) and not r.get("error")]
        error_results = [r for r in results if isinstance(r, dict) and r.get("error")]
        found_sites = [r for r in valid_results if r.get("found")]
        
        # Группируем по категориям
        by_category = {}
        for site in found_sites:
            cat = site.get("category", "unknown")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(site)
        
        # Выводим результаты
        self.print_results(username, len(valid_results), len(found_sites), len(error_results), by_category)
        
        # Создаем отчет
        report_data = {
            "username": username,
            "total_checked": len(valid_results),
            "found": len(found_sites),
            "errors": len(error_results),
            "by_category": by_category,
            "all_found": found_sites,
            "selected_categories": list(self.selected_categories),
            "timestamp": datetime.now().isoformat()
        }
        
        # Сохраняем отчет
        self.save_report(report_data, username)
    
    def print_results(self, username: str, total: int, found: int, errors: int, categories: Dict):
        """Выводит результаты поиска"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}📊 {self.locale['results']['title']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        print(f"{Fore.WHITE}{self.locale['results']['username'].format(username)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.locale['results']['sites_checked'].format(total)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.locale['results']['profiles_found'].format(found)}{Style.RESET_ALL}")
        
        if errors > 0:
            print(f"{Fore.YELLOW}{self.locale['results']['errors'].format(errors)}{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}{self.locale['results']['categories'].format(len(categories))}{Style.RESET_ALL}")
        
        if categories:
            print(f"\n{Fore.YELLOW}🏆 Найденные профили:{Style.RESET_ALL}")
            for category, sites in sorted(categories.items()):
                print(f"\n{Fore.MAGENTA}📁 {category.upper()} ({len(sites)}):{Style.RESET_ALL}")
                for site in sorted(sites, key=lambda x: x['name'])[:5]:  # Показываем первые 5
                    print(f"  • {Fore.CYAN}{site['name']}{Style.RESET_ALL}: {site['url']}")
                if len(sites) > 5:
                    print(f"  {Fore.YELLOW}... и ещё {len(sites)-5} профилей{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}{self.locale['results']['no_results']}{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    def save_report(self, data: Dict, username: str):
        """Сохраняет отчет в выбранном формате"""
        if self.export_format in ["html", "both"]:
            html_file = self.create_html_report(data, username)
            print(f"{Fore.GREEN}📄 HTML: {html_file}{Style.RESET_ALL}")
        
        if self.export_format in ["csv", "both"]:
            csv_file, summary_file = self.create_csv_report(data, username)
            print(f"{Fore.GREEN}📊 CSV: {csv_file}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}📝 TXT: {summary_file}{Style.RESET_ALL}")
    
    def create_html_report(self, data: Dict, username: str) -> str:
        """Создает HTML отчет"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"whatsmyfinder_{username}_{timestamp}.html"
        filepath = os.path.join(self.config["paths"]["reports_html"], filename)
        
        # Простой HTML шаблон
        html_content = f"""<!DOCTYPE html>
<html lang="{self.language}">
<head>
    <meta charset="UTF-8">
    <title>WhatsMyFinder Report - {username}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 20px 0; }}
        .stat-box {{ background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }}
        .category {{ margin: 20px 0; border: 1px solid #ddd; border-radius: 5px; }}
        .category-header {{ background: #34495e; color: white; padding: 10px; }}
        .site-item {{ padding: 10px; border-bottom: 1px solid #eee; }}
        .site-item:last-child {{ border-bottom: none; }}
        a {{ color: #3498db; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 WhatsMyFinder Report</h1>
        <p>Username: <strong>{username}</strong> | Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Tool by: {self.config['app']['author']} | Database: {self.config['app']['data_source']}</p>
    </div>
    
    <div class="stats">
        <div class="stat-box">
            <h3>{data['total_checked']}</h3>
            <p>Sites Checked</p>
        </div>
        <div class="stat-box">
            <h3>{data['found']}</h3>
            <p>Profiles Found</p>
        </div>
        <div class="stat-box">
            <h3>{data['errors']}</h3>
            <p>Errors</p>
        </div>
        <div class="stat-box">
            <h3>{len(data['by_category'])}</h3>
            <p>Categories</p>
        </div>
    </div>
"""
        
        if data['selected_categories']:
            html_content += f"""
    <div style="background: #e8f4fd; padding: 10px; border-radius: 5px; margin: 10px 0;">
        <strong>🔧 Filtered Categories:</strong> {', '.join(data['selected_categories'])}
    </div>
"""
        
        for category, sites in sorted(data['by_category'].items()):
            html_content += f"""
    <div class="category">
        <div class="category-header">
            <h3>{category.upper()} ({len(sites)})</h3>
        </div>
"""
            for site in sorted(sites, key=lambda x: x['name']):
                html_content += f"""
        <div class="site-item">
            <strong>{site['name']}</strong><br>
            <a href="{site['url']}" target="_blank">{site['url']}</a>
        </div>
"""
            html_content += """
    </div>
"""
        
        html_content += f"""
    <div style="margin-top: 30px; padding: 10px; background: #f5f5f5; border-radius: 5px; text-align: center;">
        <p>Generated by WhatsMyFinder v{self.config['app']['version']}</p>
        <p>Author: {self.config['app']['author']} | Source: {self.config['app']['data_source']}</p>
    </div>
</body>
</html>
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def create_csv_report(self, data: Dict, username: str) -> tuple:
        """Создает CSV и TXT отчеты"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # CSV файл
        csv_filename = f"whatsmyfinder_{username}_{timestamp}.csv"
        csv_filepath = os.path.join(self.config["paths"]["reports_csv"], csv_filename)
        
        # TXT файл
        txt_filename = f"whatsmyfinder_{username}_{timestamp}_summary.txt"
        txt_filepath = os.path.join(self.config["paths"]["reports_csv"], txt_filename)
        
        # Записываем CSV
        all_sites = []
        for category, sites in data['by_category'].items():
            for site in sites:
                all_sites.append({
                    "category": category,
                    "site_name": site['name'],
                    "url": site['url'],
                    "status": site.get('status', ''),
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        
        if all_sites:
            with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['category', 'site_name', 'url', 'status', 'timestamp']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for site in sorted(all_sites, key=lambda x: (x['category'], x['site_name'])):
                    writer.writerow(site)
        
        # Записываем TXT summary
        with open(txt_filepath, 'w', encoding='utf-8') as f:
            f.write(f"WhatsMyFinder Report - {username}\n")
            f.write("="*60 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Tool: {self.config['app']['name']} v{self.config['app']['version']}\n")
            f.write(f"Author: {self.config['app']['author']}\n")
            f.write(f"Database: {self.config['app']['data_source']}\n")
            f.write("="*60 + "\n")
            f.write(f"\n📊 STATISTICS:\n")
            f.write(f"  • Username: {username}\n")
            f.write(f"  • Sites checked: {data['total_checked']}\n")
            f.write(f"  • Profiles found: {data['found']}\n")
            f.write(f"  • Errors: {data['errors']}\n")
            f.write(f"  • Categories with results: {len(data['by_category'])}\n")
            
            if data['selected_categories']:
                f.write(f"  • Filtered categories: {', '.join(data['selected_categories'])}\n")
            
            f.write("\n" + "="*60 + "\n")
            f.write("🔗 FOUND PROFILES:\n")
            
            for category, sites in sorted(data['by_category'].items()):
                f.write(f"\n📁 {category.upper()} ({len(sites)}):\n")
                for site in sorted(sites, key=lambda x: x['name']):
                    f.write(f"  • {site['name']}\n")
                    f.write(f"    {site['url']}\n")
        
        return csv_filepath, txt_filepath
    
    def run(self):
        """Запускает приложение"""
        try:
            # Проверяем базу данных
            if not os.path.exists(self.config["paths"]["database"]):
                print(f"\n{Fore.RED}{self.locale['errors']['no_database']}{Style.RESET_ALL}")
                print(f"\n{Fore.YELLOW}Скачайте базу данных:{Style.RESET_ALL}")
                print(f"  wget https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json")
                print(f"\nИли поместите файл wmn-data.json в текущую директорию")
                
                choice = input(f"\n{Fore.YELLOW}Продолжить без базы данных? (y/n): {Style.RESET_ALL}").strip().lower()
                if choice != 'y':
                    return
            else:
                self.load_database()
            
            # Запускаем главное меню
            self.main_menu()
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}👋 Завершение работы...{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Критическая ошибка: {e}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()

def main():
    """Точка входа"""
    app = WhatsMyFinder()
    app.run()

if __name__ == "__main__":
    main()