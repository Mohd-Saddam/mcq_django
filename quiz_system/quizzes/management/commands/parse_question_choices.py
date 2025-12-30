"""
Management command to parse question text with embedded choices and create separate Choice objects.

This helps when you've pasted questions with answer choices in the question text field.
For example:
    "What is Flask?
    
    a) A JavaScript framework
    b) A Python web framework
    c) A PHP framework
    d) A CSS framework"

This command will:
1. Extract the question text (first line)
2. Parse the choices (a, b, c, d)
3. Create Choice objects for each option
4. Ask which choice(s) are correct
"""

from django.core.management.base import BaseCommand
from ...models import Question, Choice
import re


class Command(BaseCommand):
    help = 'Parse questions with embedded choices and create separate Choice objects'

    def add_arguments(self, parser):
        parser.add_argument(
            '--quiz-id',
            type=str,
            help='Process only questions from a specific quiz (UUID)',
        )
        parser.add_argument(
            '--question-id',
            type=str,
            help='Process a specific question (UUID)',
        )
        parser.add_argument(
            '--auto-yes',
            action='store_true',
            help='Automatically answer yes to all prompts',
        )

    def handle(self, *args, **options):
        quiz_id = options.get('quiz_id')
        question_id = options.get('question_id')
        auto_yes = options.get('auto_yes')

        # Get questions to process
        if question_id:
            questions = Question.objects.filter(id=question_id)
        elif quiz_id:
            questions = Question.objects.filter(quiz_id=quiz_id)
        else:
            questions = Question.objects.all()

        # Filter to MCQ questions with no choices but have embedded choices in text
        questions = questions.filter(question_type='MCQ', choices__isnull=True).distinct()
        
        if not questions.exists():
            self.stdout.write(self.style.WARNING('No questions found that need processing.'))
            return

        self.stdout.write(self.style.SUCCESS(f'\nFound {questions.count()} question(s) to process.\n'))

        processed = 0
        skipped = 0

        for question in questions:
            # Check if the question text contains embedded choices
            if not self._has_embedded_choices(question.question_text):
                skipped += 1
                continue

            self.stdout.write(self.style.WARNING(f'\n{"="*70}'))
            self.stdout.write(f'Question ID: {question.id}')
            self.stdout.write(f'Quiz: {question.quiz.title}')
            self.stdout.write(f'\nOriginal text:\n{question.question_text}\n')

            # Parse the question
            parsed = self._parse_question_with_choices(question.question_text)
            
            if not parsed['choices']:
                self.stdout.write(self.style.WARNING('Could not parse choices. Skipping.'))
                skipped += 1
                continue

            self.stdout.write(self.style.SUCCESS(f'\nParsed question text: {parsed["question"]}'))
            self.stdout.write(self.style.SUCCESS(f'Found {len(parsed["choices"])} choices:'))
            for i, choice in enumerate(parsed['choices'], 1):
                self.stdout.write(f'  {i}. {choice}')

            if not auto_yes:
                proceed = input('\nProceed with parsing this question? (y/n): ')
                if proceed.lower() != 'y':
                    skipped += 1
                    continue

            # Update question text
            question.question_text = parsed['question']
            question.save()

            # Create choices
            if auto_yes:
                # Auto-mark first choice as correct (you'll need to update this manually)
                correct_indices = [0]
                self.stdout.write(self.style.WARNING('Auto-mode: Marking first choice as correct. Please update manually!'))
            else:
                correct_input = input('Enter correct answer number(s) separated by commas (e.g., "1" or "1,3"): ')
                try:
                    correct_indices = [int(x.strip()) - 1 for x in correct_input.split(',')]
                except ValueError:
                    self.stdout.write(self.style.ERROR('Invalid input. Marking first as correct.'))
                    correct_indices = [0]

            for i, choice_text in enumerate(parsed['choices']):
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=(i in correct_indices),
                    order=i
                )

            processed += 1
            self.stdout.write(self.style.SUCCESS(f'Successfully processed question!'))

        self.stdout.write(self.style.SUCCESS(f'\n\nSummary:'))
        self.stdout.write(self.style.SUCCESS(f'  Processed: {processed}'))
        self.stdout.write(f'  Skipped: {skipped}')

    def _has_embedded_choices(self, text):
        """Check if text contains embedded choices like a), b), c), d)"""
        # Look for patterns like a), b), c) or A), B), C)
        pattern = r'[a-dA-D]\)\s*.+'
        return bool(re.search(pattern, text))

    def _parse_question_with_choices(self, text):
        """Parse question text with embedded choices"""
        lines = text.strip().split('\n')
        
        # Pattern to match choices: a), b), c), d) or A), B), C), D)
        choice_pattern = re.compile(r'^([a-dA-D])\)\s*(.+)$')
        
        question_lines = []
        choices = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            match = choice_pattern.match(line)
            if match:
                # This is a choice
                choice_text = match.group(2).strip()
                choices.append(choice_text)
            else:
                # This is part of the question
                question_lines.append(line)
        
        question = ' '.join(question_lines)
        
        return {
            'question': question,
            'choices': choices
        }
