import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from fastmcp import Server
from fastmcp.schemas import PromptInfo, MCPContext

from server.utils.config import Config
from server.utils.filesystem import FileSystemHelper

logger = logging.getLogger(__name__)

def register_prompts(server: Server, config: Config) -> None:
    """Register file-related prompts with the MCP server."""
    fs_helper = FileSystemHelper(config)
    
    @server.prompt("file.code_review")
    async def code_review_prompt(context: MCPContext) -> PromptInfo:
        """
        Generate a prompt for code review of a file or set of files.
        
        This prompt analyzes file content and provides context needed for 
        LLMs to perform effective code reviews.
        """
        logger.info("Using code review prompt")
        
        # Get file URI parameter if provided
        file_uri = context.parameters.get("file_uri", None)
        file_content = None
        file_metadata = None
        
        if file_uri:
            if file_uri.startswith("file://"):
                path_str = file_uri[7:]
                file_path, is_valid = fs_helper.normalize_path(path_str)
                
                if is_valid and file_path.exists() and file_path.is_file():
                    file_content = fs_helper.read_file(file_path)
                    file_metadata = fs_helper.get_file_metadata(file_path)
        
        system_prompt = """
        You are a code review assistant analyzing the provided file(s). 
        Your task is to perform a thorough code review focusing on:
        
        1. Code quality and best practices
        2. Potential bugs or issues
        3. Performance concerns
        4. Security vulnerabilities
        5. Maintainability and readability
        6. Suggestions for improvement
        
        For each issue identified, explain why it's a concern and suggest a specific improvement.
        If the code follows best practices in certain areas, acknowledge those as well.
        
        Format your review in a clear, structured manner with separate sections for different types of feedback.
        If no file content is provided, assist the user in selecting files to review.
        """
        
        if file_content:
            file_name = file_metadata.get("name", "Unknown file")
            file_type = file_metadata.get("extension", "")
            file_lang = "Unknown"
            
            # Infer language from file extension
            if file_type.lower() in ["py", "pyw"]:
                file_lang = "Python"
            elif file_type.lower() in ["js", "jsx", "ts", "tsx"]:
                file_lang = "JavaScript/TypeScript"
            elif file_type.lower() in ["java"]:
                file_lang = "Java"
            elif file_type.lower() in ["c", "cpp", "h", "hpp"]:
                file_lang = "C/C++"
            elif file_type.lower() in ["go"]:
                file_lang = "Go"
            elif file_type.lower() in ["rb"]:
                file_lang = "Ruby"
            elif file_type.lower() in ["php"]:
                file_lang = "PHP"
            elif file_type.lower() in ["rs"]:
                file_lang = "Rust"
            elif file_type.lower() in ["html", "htm"]:
                file_lang = "HTML"
            elif file_type.lower() in ["css", "scss", "sass"]:
                file_lang = "CSS"
            
            user_prompt = f"""
            Please review the following {file_lang} code from file '{file_name}':
            
            ```{file_type}
            {file_content}
            ```
            """
        else:
            user_prompt = """
            I'd like you to review some code for me. 
            I'll either share a file path or paste the code directly.
            
            Please help me improve the code quality, identify issues, and suggest enhancements.
            """
        
        return PromptInfo(
            system=system_prompt.strip(),
            user=user_prompt.strip()
        )
    
    @server.prompt("file.summarize")
    async def summarize_file_prompt(context: MCPContext) -> PromptInfo:
        """
        Generate a prompt for summarizing a file's content.
        
        This prompt helps LLMs generate concise summaries of files
        with appropriate context about the file type.
        """
        logger.info("Using file summarization prompt")
        
        # Get file URI parameter if provided
        file_uri = context.parameters.get("file_uri", None)
        file_content = None
        file_metadata = None
        
        if file_uri:
            if file_uri.startswith("file://"):
                path_str = file_uri[7:]
                file_path, is_valid = fs_helper.normalize_path(path_str)
                
                if is_valid and file_path.exists() and file_path.is_file():
                    file_content = fs_helper.read_file(file_path)
                    file_metadata = fs_helper.get_file_metadata(file_path)
        
        system_prompt = """
        You are a document summarization assistant. Your task is to provide concise, accurate summaries 
        of file contents while preserving the key information. Adapt your summarization approach based on the file type:
        
        - For code files: Explain the purpose, main components, functions, and overall architecture
        - For documentation: Extract key points, main topics, and important details
        - For data files: Describe the structure, content type, and significant patterns
        - For configuration: Highlight important settings and their implications
        
        Your summary should be comprehensive enough to give a clear understanding of the file's purpose 
        and content, but brief enough to provide value over reading the entire file.
        
        If the file is too large or complex for a single summary, provide a high-level overview
        and then summarize key sections separately.
        """
        
        if file_content:
            file_name = file_metadata.get("name", "Unknown file")
            file_type = file_metadata.get("extension", "")
            mime_type = file_metadata.get("mime_type", "Unknown")
            
            user_prompt = f"""
            Please summarize the following file:
            
            File name: {file_name}
            File type: {file_type}
            MIME type: {mime_type}
            
            Content:
            ```
            {file_content}
            ```
            """
        else:
            user_prompt = """
            I'd like you to summarize a file for me.
            Please provide a concise yet comprehensive summary that captures the main points and purpose of the file.
            
            I'll either share a file path or paste the content directly.
            """
        
        return PromptInfo(
            system=system_prompt.strip(),
            user=user_prompt.strip()
        )
    
    @server.prompt("file.project_structure")
    async def project_structure_prompt(context: MCPContext) -> PromptInfo:
        """
        Generate a prompt for analyzing project structure.
        
        This prompt helps LLMs analyze and provide insights about
        the structure of files and directories in a project.
        """
        logger.info("Using project structure analysis prompt")
        
        # Get directory URI parameter if provided
        dir_uri = context.parameters.get("directory_uri", None)
        dir_structure = None
        dir_path_str = None
        
        if dir_uri:
            if dir_uri.startswith("file://"):
                dir_path_str = dir_uri[7:]
                dir_path, is_valid = fs_helper.normalize_path(dir_path_str)
                
                if is_valid and dir_path.exists() and dir_path.is_dir():
                    try:
                        # Get directory structure recursively
                        dir_listing = fs_helper.list_directory(dir_path, recursive=True, max_depth=5)
                        
                        # Convert to a tree-like structure
                        dir_structure = {
                            "path": str(dir_path),
                            "name": dir_path.name,
                            "items": dir_listing,
                            "count": len(dir_listing)
                        }
                    except Exception as e:
                        logger.error(f"Error getting directory structure: {e}")
        
        system_prompt = """
        You are a project structure analysis assistant. Your task is to analyze the directory structure
        of a software project and provide insights about its organization, architecture, and potential improvements.
        
        When analyzing a project structure:
        
        1. Identify the main components and their responsibilities
        2. Recognize the architectural pattern being used (if any)
        3. Detect common directories and their purposes (e.g., src, tests, docs)
        4. Highlight strengths and potential issues in the organization
        5. Suggest improvements for better maintainability and clarity
        
        Focus on providing a clear understanding of how the project is organized and how the different
        parts relate to each other. If appropriate, suggest reorganization that might improve the project.
        """
        
        if dir_structure:
            # Format directory structure for display
            formatted_structure = []
            
            # Group items by directory
            dir_dict = {}
            for item in dir_structure["items"]:
                path_parts = item["path"].split("/")
                current_level = dir_dict
                
                # Build a nested dictionary representing the directory structure
                for i, part in enumerate(path_parts[:-1]):
                    if part not in current_level:
                        current_level[part] = {}
                    current_level = current_level[part]
                
                # Add the file or empty dict for directory
                if "mime_type" in item and item["mime_type"] != "inode/directory":
                    current_level[path_parts[-1]] = item["mime_type"]
                else:
                    current_level[path_parts[-1]] = {}
            
            # Function to format the nested dictionary as a tree
            def format_tree(d, indent=0):
                result = []
                for k, v in sorted(d.items()):
                    if isinstance(v, dict):
                        result.append("  " * indent + f"📁 {k}/")
                        result.extend(format_tree(v, indent + 1))
                    else:
                        result.append("  " * indent + f"📄 {k} ({v})")
                return result
            
            formatted_structure = format_tree(dir_dict)
            
            user_prompt = f"""
            Please analyze the following project structure for {dir_path_str}:
            
            ```
            {"".join(f"{line}\n" for line in formatted_structure)}
            ```
            
            Provide insights about the project organization, identify the main components,
            detect the architectural patterns in use, and suggest any improvements that could
            make the structure more maintainable or clearer.
            """
        else:
            user_prompt = """
            I'd like you to analyze the structure of a project directory.
            
            Please provide insights about:
            - The overall organization
            - Architectural patterns used
            - Main components and their responsibilities
            - Potential improvements to the structure
            
            I'll either share a directory path or describe the structure.
            """
        
        return PromptInfo(
            system=system_prompt.strip(),
            user=user_prompt.strip()
        )