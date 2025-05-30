#!/usr/bin/env python3
import os
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
import fnmatch
import sys
import termios
import tty

@dataclass
class CommentConfig:
    include_text_comments: bool = True
    include_commented_code: bool = True
    strip_comment_markers: bool = False
    preserve_comment_structure: bool = True

@dataclass
class ProfileConfig:
    name: str
    include_patterns: List[str]
    exclude_patterns: List[str]
    include_tree: bool
    max_file_size: int
    encoding: str
    add_line_numbers: bool
    include_hidden: bool
    tree_depth: Optional[int]
    custom_header: str
    custom_footer: str
    comment_config: CommentConfig

class ConfigManager:
    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path.home() / '.llmtree'
        self.config_file = self.config_dir / 'config.json'
        self.ensure_config_dir()
        
    def ensure_config_dir(self):
        self.config_dir.mkdir(exist_ok=True)
        
    def load_config(self) -> Dict[str, ProfileConfig]:
        if not self.config_file.exists():
            return self._create_default_config()
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                profiles = {}
                for name, config in data.items():
                    if 'comment_config' not in config:
                        config['comment_config'] = {
                            'include_text_comments': True,
                            'include_commented_code': True,
                            'strip_comment_markers': False,
                            'preserve_comment_structure': True
                        }
                    
                    comment_config = CommentConfig(**config['comment_config'])
                    del config['comment_config']
                    profile = ProfileConfig(**config, comment_config=comment_config)
                    profiles[name] = profile
                return profiles
        except Exception:
            return self._create_default_config()
    
    def save_config(self, profiles: Dict[str, ProfileConfig]):
        config_data = {
            name: asdict(profile) 
            for name, profile in profiles.items()
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def _create_default_config(self) -> Dict[str, ProfileConfig]:
        default_comment_config = CommentConfig(
            include_text_comments=True,
            include_commented_code=True,
            strip_comment_markers=False,
            preserve_comment_structure=True
        )
        
        default_profile = ProfileConfig(
            name="default",
            include_patterns=["*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.vue", 
                            "*.java", "*.cpp", "*.c", "*.h", "*.cs", "*.rb", 
                            "*.php", "*.go", "*.rs", "*.swift", "*.kt", "*.scala",
                            "*.md", "*.txt", "*.yml", "*.yaml", "*.json", "*.xml",
                            "*.html", "*.css", "*.scss", "*.sass", "*.less"],
            exclude_patterns=["node_modules/*", ".git/*", "__pycache__/*", 
                            "*.pyc", "*.pyo", ".venv/*", "venv/*", ".env",
                            "dist/*", "build/*", "target/*", ".idea/*", 
                            ".vscode/*", "*.log", "*.tmp"],
            include_tree=True,
            max_file_size=100000,
            encoding='utf-8',
            add_line_numbers=False,
            include_hidden=False,
            tree_depth=3,
            custom_header="",
            custom_footer="",
            comment_config=default_comment_config
        )
        
        python_comment_config = CommentConfig(
            include_text_comments=True,
            include_commented_code=False,
            strip_comment_markers=False,
            preserve_comment_structure=True
        )
        
        python_profile = ProfileConfig(
            name="python",
            include_patterns=["*.py", "*.pyx", "*.pyi", "requirements.txt", 
                            "setup.py", "pyproject.toml", "*.md"],
            exclude_patterns=["__pycache__/*", "*.pyc", "*.pyo", ".venv/*", 
                            "venv/*", ".pytest_cache/*", "*.egg-info/*"],
            include_tree=True,
            max_file_size=50000,
            encoding='utf-8',
            add_line_numbers=True,
            include_hidden=False,
            tree_depth=2,
            custom_header="# Python Project Analysis\n",
            custom_footer="",
            comment_config=python_comment_config
        )
        
        profiles = {"default": default_profile, "python": python_profile}
        self.save_config(profiles)
        return profiles

class CommentProcessor:
    LANGUAGE_CONFIGS = {
        'py': {'single': '#', 'multi_start': '"""', 'multi_end': '"""', 'alt_multi': ("'''", "'''")},
        'js': {'single': '//', 'multi_start': '/*', 'multi_end': '*/'},
        'ts': {'single': '//', 'multi_start': '/*', 'multi_end': '*/'},
        'jsx': {'single': '//', 'multi_start': '/*', 'multi_end': '*/'},
        'tsx': {'single': '//', 'multi_start': '/*', 'multi_end': '*/'},
        'java': {'single': '//', 'multi_start': '/*', 'multi_end': '*/'},
        'cpp': {'single': '//', 'multi_start': '/*', 'multi_end': '*/'},
        'c': {'single': '//', 'multi_start': '/*', 'multi_end': '*/'},
        'h': {'single': '//', 'multi_start': '/*', 'multi_end': '*/'},
        'cs': {'single': '//', 'multi_start': '/*', 'multi_end': '*/'},
        'php': {'single': '//', 'multi_start': '/*', 'multi_end': '*/', 'alt_single': '#'},
        'rb': {'single': '#', 'multi_start': '=begin', 'multi_end': '=end'},
        'go': {'single': '//', 'multi_start': '/*', 'multi_end': '*/'},
        'rs': {'single': '//', 'multi_start': '/*', 'multi_end': '*/'},
        'swift': {'single': '//', 'multi_start': '/*', 'multi_end': '*/'},
        'kt': {'single': '//', 'multi_start': '/*', 'multi_end': '*/'},
        'scala': {'single': '//', 'multi_start': '/*', 'multi_end': '*/'},
        'sql': {'single': '--', 'multi_start': '/*', 'multi_end': '*/'},
        'sh': {'single': '#'},
        'bash': {'single': '#'},
        'zsh': {'single': '#'},
        'ps1': {'single': '#', 'multi_start': '<#', 'multi_end': '#>'},
        'html': {'multi_start': '<!--', 'multi_end': '-->'},
        'xml': {'multi_start': '<!--', 'multi_end': '-->'},
        'css': {'multi_start': '/*', 'multi_end': '*/'},
        'scss': {'single': '//', 'multi_start': '/*', 'multi_end': '*/'},
        'sass': {'single': '//'},
        'less': {'single': '//', 'multi_start': '/*', 'multi_end': '*/'},
        'vue': {'multi_start': '<!--', 'multi_end': '-->', 'script_single': '//', 'script_multi': ('/*', '*/')},
        'yml': {'single': '#'},
        'yaml': {'single': '#'},
        'toml': {'single': '#'},
        'ini': {'single': ';', 'alt_single': '#'},
        'cfg': {'single': '#'},
        'conf': {'single': '#'},
    }
    
    def __init__(self, comment_config: CommentConfig):
        self.config = comment_config
        
    def process_file_content(self, content: str, file_extension: str) -> str:
        if not any([self.config.include_text_comments, self.config.include_commented_code]):
            return content
            
        lang_config = self.LANGUAGE_CONFIGS.get(file_extension.lower(), {})
        if not lang_config:
            return content
            
        lines = content.split('\n')
        processed_lines = []
        in_multiline = False
        multiline_markers = None
        
        for line in lines:
            processed_line = self._process_line(
                line, lang_config, in_multiline, multiline_markers
            )
            
            if processed_line['update_multiline']:
                in_multiline = processed_line['in_multiline']
                multiline_markers = processed_line['multiline_markers']
                
            if processed_line['include']:
                processed_lines.append(processed_line['content'])
                
        return '\n'.join(processed_lines)
    
    def _process_line(self, line: str, lang_config: dict, in_multiline: bool, 
                     multiline_markers: tuple) -> dict:
        stripped = line.strip()
        result = {
            'content': line,
            'include': True,
            'update_multiline': False,
            'in_multiline': in_multiline,
            'multiline_markers': multiline_markers
        }
        
        if in_multiline:
            if multiline_markers and multiline_markers[1] in line:
                result['update_multiline'] = True
                result['in_multiline'] = False
                result['multiline_markers'] = None
                
            comment_type = self._classify_multiline_content(line, multiline_markers)
            if not self._should_include_comment(comment_type):
                result['include'] = False
                
            if result['include'] and self.config.strip_comment_markers:
                result['content'] = self._strip_multiline_markers(line, multiline_markers)
                
            return result
            
        for marker_key in ['multi_start', 'alt_multi']:
            if marker_key in lang_config:
                markers = lang_config[marker_key]
                if isinstance(markers, tuple):
                    start_marker, end_marker = markers
                else:
                    start_marker = markers
                    end_marker = lang_config.get('multi_end', '')
                    
                if start_marker in line:
                    result['update_multiline'] = True
                    result['in_multiline'] = True
                    result['multiline_markers'] = (start_marker, end_marker)
                    
                    if end_marker in line and line.find(end_marker) > line.find(start_marker):
                        result['in_multiline'] = False
                        result['multiline_markers'] = None
                        
                    comment_type = self._classify_multiline_content(line, (start_marker, end_marker))
                    if not self._should_include_comment(comment_type):
                        result['include'] = False
                        
                    if result['include'] and self.config.strip_comment_markers:
                        result['content'] = self._strip_multiline_markers(line, (start_marker, end_marker))
                        
                    return result
        
        single_markers = []
        if 'single' in lang_config:
            single_markers.append(lang_config['single'])
        if 'alt_single' in lang_config:
            single_markers.append(lang_config['alt_single'])
            
        for marker in single_markers:
            if stripped.startswith(marker):
                comment_type = self._classify_single_line_content(line, marker)
                if not self._should_include_comment(comment_type):
                    result['include'] = False
                    
                if result['include'] and self.config.strip_comment_markers:
                    result['content'] = self._strip_single_line_marker(line, marker)
                    
                return result
                
        return result
    
    def _classify_single_line_content(self, line: str, marker: str) -> str:
        comment_content = line.split(marker, 1)[1].strip()
        
        code_indicators = [
            '=', '()', '[]', '{}', ';', 'def ', 'class ', 'function ', 'var ', 'let ',
            'const ', 'if ', 'for ', 'while ', 'return ', 'import ', 'from ', 'include'
        ]
        
        text_indicators = [
            'TODO', 'FIXME', 'NOTE', 'WARNING', 'BUG', 'HACK', 'XXX',
            '?', '!', 'Description', 'Author', 'Version'
        ]
        
        code_score = sum(1 for indicator in code_indicators if indicator in comment_content)
        text_score = sum(1 for indicator in text_indicators if indicator.upper() in comment_content.upper())
        
        if any(comment_content.strip().startswith(prefix) for prefix in ['def ', 'class ', 'function ', 'var ']):
            return 'code'
        if len(comment_content.split()) < 3 and ('=' in comment_content or '()' in comment_content):
            return 'code'
        if text_score > 0:
            return 'text'
        if code_score > text_score:
            return 'code'
            
        return 'text'
    
    def _classify_multiline_content(self, line: str, markers: tuple) -> str:
        if not markers:
            return 'text'
            
        start_marker, end_marker = markers
        content = line
        
        if start_marker in content:
            content = content.split(start_marker, 1)[1]
        if end_marker in content:
            content = content.rsplit(end_marker, 1)[0]
            
        content = content.strip()
        
        if content and (content[0].isupper() or content.startswith(('@', 'Args:', 'Returns:', 'Raises:'))):
            return 'text'
            
        code_indicators = ['def ', 'class ', 'function ', '= ', '()', 'import ', 'from ']
        if any(indicator in content for indicator in code_indicators):
            return 'code'
            
        return 'text'
    
    def _should_include_comment(self, comment_type: str) -> bool:
        if comment_type == 'text':
            return self.config.include_text_comments
        elif comment_type == 'code':
            return self.config.include_commented_code
        return True
    
    def _strip_single_line_marker(self, line: str, marker: str) -> str:
        if not self.config.preserve_comment_structure:
            return line.split(marker, 1)[1].strip()
        return line.replace(marker, '', 1).lstrip()
    
    def _strip_multiline_markers(self, line: str, markers: tuple) -> str:
        start_marker, end_marker = markers
        result = line
        
        if start_marker in result:
            result = result.replace(start_marker, '', 1)
        if end_marker in result:
            result = result.replace(end_marker, '', 1)
            
        if not self.config.preserve_comment_structure:
            result = result.strip()
            
        return result

class FileProcessor:
    def __init__(self, profile: ProfileConfig):
        self.profile = profile
        self.comment_processor = CommentProcessor(profile.comment_config)
        
    def should_include_file(self, file_path: Path, base_path: Path) -> bool:
        relative_path = file_path.relative_to(base_path)
        path_str = str(relative_path).replace('\\', '/')
        
        if not self.profile.include_hidden and any(
            part.startswith('.') for part in relative_path.parts
        ):
            return False
            
        if file_path.is_file() and file_path.stat().st_size > self.profile.max_file_size:
            return False
            
        for pattern in self.profile.exclude_patterns:
            if fnmatch.fnmatch(path_str, pattern):
                return False
                
        for pattern in self.profile.include_patterns:
            if fnmatch.fnmatch(path_str, pattern):
                return True
                
        return False
    
    def read_file_content(self, file_path: Path) -> Optional[str]:
        try:
            with open(file_path, 'r', encoding=self.profile.encoding, errors='ignore') as f:
                content = f.read()
                
            file_ext = file_path.suffix[1:] if file_path.suffix else 'text'
            content = self.comment_processor.process_file_content(content, file_ext)
                
            if self.profile.add_line_numbers:
                lines = content.split('\n')
                content = '\n'.join(f"{i+1:4}: {line}" for i, line in enumerate(lines))
                
            return content
        except Exception as e:
            return f"Error reading file: {e}"
    
    def get_tree_structure(self, path: Path) -> Optional[str]:
        if not self.profile.include_tree:
            return None
            
        try:
            cmd = ['tree', str(path)]
            if self.profile.tree_depth:
                cmd.extend(['-L', str(self.profile.tree_depth)])
            if not self.profile.include_hidden:
                cmd.append('-a')
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.stdout if result.returncode == 0 else None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return self._fallback_tree(path)
    
    def _fallback_tree(self, path: Path, prefix: str = "", max_depth: int = None) -> str:
        if max_depth is not None and max_depth <= 0:
            return ""
            
        items = []
        try:
            for item in sorted(path.iterdir()):
                if not self.profile.include_hidden and item.name.startswith('.'):
                    continue
                    
                is_last = item == sorted(path.iterdir())[-1]
                current_prefix = "└── " if is_last else "├── "
                items.append(f"{prefix}{current_prefix}{item.name}")
                
                if item.is_dir():
                    extension = "    " if is_last else "│   "
                    next_depth = None if max_depth is None else max_depth - 1
                    items.append(self._fallback_tree(
                        item, prefix + extension, next_depth
                    ))
        except PermissionError:
            pass
            
        return '\n'.join(filter(None, items))

class LLMTreeGenerator:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.profiles = config_manager.load_config()
        
    def generate_output(self, target_path: Path, profile_name: str = "default") -> str:
        if profile_name not in self.profiles:
            profile_name = "default"
            
        profile = self.profiles[profile_name]
        processor = FileProcessor(profile)
        
        output_parts = []
        
        if profile.custom_header:
            output_parts.append(profile.custom_header)
            
        tree_structure = processor.get_tree_structure(target_path)
        if tree_structure:
            output_parts.extend([
                "## Project Structure\n",
                "```",
                tree_structure,
                "```\n"
            ])
            
        output_parts.append("## Source Files\n")
        
        files_processed = 0
        for file_path in self._walk_directory(target_path):
            if processor.should_include_file(file_path, target_path):
                relative_path = file_path.relative_to(target_path)
                content = processor.read_file_content(file_path)
                
                if content:
                    file_ext = file_path.suffix[1:] if file_path.suffix else 'text'
                    output_parts.extend([
                        f"### {relative_path}\n",
                        f"```{file_ext}",
                        content,
                        "```\n"
                    ])
                    files_processed += 1
                    
        if files_processed == 0:
            output_parts.append("No files found matching the current profile criteria.\n")
            
        if profile.custom_footer:
            output_parts.append(profile.custom_footer)
            
        return '\n'.join(output_parts)
    
    def _walk_directory(self, path: Path):
        for root, dirs, files in os.walk(path):
            root_path = Path(root)
            for file in files:
                yield root_path / file

class InteractiveManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        
    def run_interactive_setup(self):
        while True:
            self._show_main_menu()
            choice = input("Choice: ").strip()
            
            if choice == '1':
                self._list_profiles()
            elif choice == '2':
                self._create_profile()
            elif choice == '3':
                self._edit_profile()
            elif choice == '4':
                self._delete_profile()
            elif choice == '5':
                self._test_profile()
            elif choice == '6':
                self._configure_comments()
            elif choice == 'q':
                break
            else:
                print("Invalid choice. Please try again.")
                
    def _show_main_menu(self):
        print("\n" + "="*50)
        print("LLM Tree Configuration")
        print("="*50)
        print("1. List profiles")
        print("2. Create new profile")
        print("3. Edit profile")
        print("4. Delete profile")
        print("5. Test profile")
        print("6. Configure comment processing")
        print("q. Quit")
        print("-"*50)
        
    def _list_profiles(self):
        profiles = self.config_manager.load_config()
        print(f"\nAvailable profiles ({len(profiles)}):")
        for name, profile in profiles.items():
            print(f"  • {name}")
            print(f"    Include: {', '.join(profile.include_patterns[:3])}...")
            print(f"    Tree: {'Yes' if profile.include_tree else 'No'}")
            print(f"    Comments: Text={profile.comment_config.include_text_comments}, Code={profile.comment_config.include_commented_code}")
            
    def _create_profile(self):
        name = input("Profile name: ").strip()
        if not name:
            print("Profile name cannot be empty.")
            return
            
        profiles = self.config_manager.load_config()
        if name in profiles:
            print(f"Profile '{name}' already exists.")
            return
            
        profile = self._configure_profile(name)
        profiles[name] = profile
        self.config_manager.save_config(profiles)
        print(f"Profile '{name}' created successfully.")
        
    def _edit_profile(self):
        profiles = self.config_manager.load_config()
        name = input("Profile name to edit: ").strip()
        
        if name not in profiles:
            print(f"Profile '{name}' not found.")
            return
            
        profile = self._configure_profile(name, profiles[name])
        profiles[name] = profile
        self.config_manager.save_config(profiles)
        print(f"Profile '{name}' updated successfully.")
        
    def _delete_profile(self):
        profiles = self.config_manager.load_config()
        name = input("Profile name to delete: ").strip()
        
        if name not in profiles:
            print(f"Profile '{name}' not found.")
            return
            
        if name == "default":
            print("Cannot delete the default profile.")
            return
            
        confirm = input(f"Delete profile '{name}'? (y/N): ").strip().lower()
        if confirm == 'y':
            del profiles[name]
            self.config_manager.save_config(profiles)
            print(f"Profile '{name}' deleted.")
            
    def _configure_profile(self, name: str, existing: ProfileConfig = None) -> ProfileConfig:
        if existing:
            profile = existing
        else:
            profile = ProfileConfig(
                name=name, include_patterns=[], exclude_patterns=[],
                include_tree=True, max_file_size=100000, encoding='utf-8',
                add_line_numbers=False, include_hidden=False, tree_depth=3,
                custom_header="", custom_footer="",
                comment_config=CommentConfig()
            )
            
        print(f"\nConfiguring profile: {name}")
        
        patterns = input(f"Include patterns [{','.join(profile.include_patterns)}]: ").strip()
        if patterns:
            profile.include_patterns = [p.strip() for p in patterns.split(',')]
            
        excludes = input(f"Exclude patterns [{','.join(profile.exclude_patterns)}]: ").strip()
        if excludes:
            profile.exclude_patterns = [p.strip() for p in excludes.split(',')]
            
        tree_input = input(f"Include tree structure? (y/n) [{profile.include_tree}]: ").strip().lower()
        if tree_input in ('y', 'n'):
            profile.include_tree = tree_input == 'y'
            
        size_input = input(f"Max file size [{profile.max_file_size}]: ").strip()
        if size_input.isdigit():
            profile.max_file_size = int(size_input)
            
        text_comments = input(f"Include text comments? (y/n) [{profile.comment_config.include_text_comments}]: ").strip().lower()
        if text_comments in ('y', 'n'):
            profile.comment_config.include_text_comments = text_comments == 'y'
            
        code_comments = input(f"Include commented code? (y/n) [{profile.comment_config.include_commented_code}]: ").strip().lower()
        if code_comments in ('y', 'n'):
            profile.comment_config.include_commented_code = code_comments == 'y'
            
        strip_markers = input(f"Strip comment markers? (y/n) [{profile.comment_config.strip_comment_markers}]: ").strip().lower()
        if strip_markers in ('y', 'n'):
            profile.comment_config.strip_comment_markers = strip_markers == 'y'
            
        return profile
        
    def _test_profile(self):
        profiles = self.config_manager.load_config()
        name = input("Profile name to test: ").strip()
        
        if name not in profiles:
            print(f"Profile '{name}' not found.")
            return
            
        test_path = Path(input("Test path [.]: ").strip() or ".")
        if not test_path.exists():
            print("Path does not exist.")
            return
            
        generator = LLMTreeGenerator(self.config_manager)
        output = generator.generate_output(test_path, name)
        
        print(f"\nTest output (first 500 chars):")
        print("-" * 50)
        print(output[:500])
        if len(output) > 500:
            print("...")
        print(f"\nTotal length: {len(output)} characters")
        
    def _configure_comments(self):
        profiles = self.config_manager.load_config()
        print("\nAvailable profiles:")
        for i, name in enumerate(profiles.keys(), 1):
            print(f"{i}. {name}")
            
        try:
            choice = int(input("Select profile to configure comments: ").strip())
            profile_names = list(profiles.keys())
            if 1 <= choice <= len(profile_names):
                profile_name = profile_names[choice - 1]
                profile = profiles[profile_name]
                
                print(f"\nConfiguring comments for profile: {profile_name}")
                print("Current settings:")
                print(f"  Text comments: {profile.comment_config.include_text_comments}")
                print(f"  Commented code: {profile.comment_config.include_commented_code}")
                print(f"  Strip markers: {profile.comment_config.strip_comment_markers}")
                print(f"  Preserve structure: {profile.comment_config.preserve_comment_structure}")
                
                text_input = input("Include text comments (y/n): ").strip().lower()
                if text_input in ('y', 'n'):
                    profile.comment_config.include_text_comments = text_input == 'y'
                    
                code_input = input("Include commented code (y/n): ").strip().lower()
                if code_input in ('y', 'n'):
                    profile.comment_config.include_commented_code = code_input == 'y'
                    
                strip_input = input("Strip comment markers (y/n): ").strip().lower()
                if strip_input in ('y', 'n'):
                    profile.comment_config.strip_comment_markers = strip_input == 'y'
                    
                preserve_input = input("Preserve comment structure (y/n): ").strip().lower()
                if preserve_input in ('y', 'n'):
                    profile.comment_config.preserve_comment_structure = preserve_input == 'y'
                    
                self.config_manager.save_config(profiles)
                print(f"Comment configuration for '{profile_name}' updated successfully.")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")

def get_single_char():
    """Читает один символ без нажатия Enter (только для Unix/macOS)"""
    try:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return char
    except:
        # Fallback для Windows или если что-то пошло не так
        return input().strip()

def main():
    parser = argparse.ArgumentParser(description="Generate LLM-ready project documentation")
    parser.add_argument("path", nargs="?", default=".", 
                       help="Target directory path (default: current directory)")
    parser.add_argument("-p", "--profile", default="default", 
                       help="Profile to use (default: default)")
    parser.add_argument("-o", "--output", default="4llm.md", 
                       help="Output file name (default: 4llm.md)")
    parser.add_argument("--config", action="store_true", 
                       help="Run interactive configuration")
    
    args = parser.parse_args()
    
    config_manager = ConfigManager()
    
    if args.config:
        interactive = InteractiveManager(config_manager)
        interactive.run_interactive_setup()
        return
        
    target_path = Path(args.path).resolve()
    if not target_path.exists():
        print(f"Error: Path '{target_path}' does not exist.")
        sys.exit(1)
        
    print(f"Processing: {target_path}")
    print("Press SPACE for configuration or ENTER to generate...")
    
    try:
        key = get_single_char()
        
        if key == ' ':
            print("\nOpening configuration...")
            interactive = InteractiveManager(config_manager)
            interactive.run_interactive_setup()
            return
        elif key == '\r' or key == '\n' or key == '':
            print("\nGenerating documentation...")
        else:
            print(f"\nUnknown key '{key}', generating documentation...")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        return
        
    generator = LLMTreeGenerator(config_manager)
    output = generator.generate_output(target_path, args.profile)
    
    output_file = target_path / args.output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)
        
    print(f"Generated: {output_file}")
    print(f"Size: {len(output)} characters")


if __name__ == "__main__":
    main()