# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a UI mockups repository for the Dewey and Ethical Capital platforms. It contains HTML prototypes, Django integration templates, and style guidelines for building data-dense, keyboard-centric financial analysis interfaces.

## Repository Structure

The codebase is organized into three main directories:

- **`public facing/`** - Customer-facing templates and Django integration files
- **`issues to fix/`** - UI mockups that need refinement or fixes  
- **`research_workbench/`** - Internal analysis and research tools

## Key Technical Stack

- **Frontend**: Standalone HTML with inline CSS following the Dewey design system
- **Backend Integration**: Django templates with Python views
- **Styling**: CSS variables-based design system (monospace, data-dense)
- **Performance**: Server-side rendering focus, minimal JavaScript

## Design System

The Dewey platform follows these core principles (detailed in `dewey-style-guide.md`):

1. **Data Density + Speed**: Information-rich interfaces with sub-100ms response times
2. **Keyboard-Centric**: Every action has a hotkey (J/K navigation, ? for help)
3. **Performance First**: No animations, server-side rendering, minimal JS
4. **Clear Hierarchy**: Purple branding (#553C9A), semantic colors for data

## Common Development Tasks

Since this is a static mockup repository, there are no build or test commands. For development:

1. **Viewing Mockups**: Open HTML files directly in a browser
2. **Editing Styles**: CSS is inline within each HTML file following the design system
3. **Django Integration**: Refer to files in `public facing/` for Django template examples

## Django Integration Patterns

When converting mockups to Django:

1. Use the template patterns from `public facing/django_*.py` files
2. Follow the unified content template structure shown in `django-content-integration.md`
3. Implement server-side rendering for performance as shown in `research_workbench/server_side_render.html`

## Important Notes

- Avoid using obscure port numbers as mentioned in existing instructions
- Follow the monospace, data-dense design aesthetic throughout
- Prioritize keyboard navigation and performance over visual effects
- All interactive elements should have visible hotkey hints