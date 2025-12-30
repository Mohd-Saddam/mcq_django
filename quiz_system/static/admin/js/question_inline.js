// JavaScript to inject "Copy from Existing Question" dropdown into question inlines
(function($) {
    'use strict';
    
    var questionsData = null;
    
    $(document).ready(function() {
        // Fetch all questions first, then inject dropdowns
        fetchAllQuestions(function() {
            injectCopyDropdowns();
        });
        
        // Also inject when new inline forms are added
        $(document).on('formset:added', function(event, $row) {
            setTimeout(function() {
                injectCopyDropdowns();
            }, 100);
        });
    });
    
    function fetchAllQuestions(callback) {
        $.ajax({
            url: '/api/questions/',
            method: 'GET',
            success: function(data) {
                questionsData = data.questions || [];
                callback();
            },
            error: function() {
                console.error('Failed to fetch questions');
                questionsData = [];
                callback();
            }
        });
    }
    
    function injectCopyDropdowns() {
        // Find all question inlines
        $('.inline-related:not(.empty-form)').each(function() {
            var $inline = $(this);
            
            // Skip if already has dropdown or is an existing question (has id)
            if ($inline.find('.copy-from-dropdown').length > 0) {
                return;
            }
            
            // Check if this is a new question (no id field value)
            var $idField = $inline.find('input[name$="-id"]');
            if ($idField.length && $idField.val()) {
                // This is an existing question, don't show copy dropdown
                return;
            }
            
            // Build dropdown HTML
            var dropdownHtml = '<div class="form-row field-copy_from copy-from-dropdown">' +
                '<label>Copy from Existing Question:</label>' +
                '<select class="copy-from-select">' +
                '<option value="">--- Create New Question (Manual Entry) ---</option>';
            
            if (questionsData && questionsData.length > 0) {
                for (var i = 0; i < questionsData.length; i++) {
                    var q = questionsData[i];
                    dropdownHtml += '<option value="' + q.id + '" data-text="' + escapeHtml(q.question_text) + '" data-type="' + q.question_type + '" data-points="' + q.points + '">' + escapeHtml(q.label) + '</option>';
                }
            }
            
            dropdownHtml += '</select>' +
                '<p class="help">Select an existing question to auto-fill the form below, or leave blank to create new</p>' +
                '</div>';
            
            // Find the fieldset and insert at the beginning
            var $fieldset = $inline.find('fieldset.module');
            if ($fieldset.length) {
                $fieldset.prepend(dropdownHtml);
            } else {
                // Fallback: insert before first form-row
                var $firstRow = $inline.find('.form-row').first();
                if ($firstRow.length) {
                    $firstRow.before(dropdownHtml);
                }
            }
            
            // Add change handler
            $inline.find('.copy-from-select').on('change', function() {
                handleCopyFromChange($(this), $inline);
            });
        });
    }
    
    function handleCopyFromChange($select, $inline) {
        var selectedOption = $select.find('option:selected');
        
        // Remove any existing info messages
        $inline.find('.reuse-info').remove();
        
        if (selectedOption.val()) {
            var questionText = selectedOption.data('text');
            var questionType = selectedOption.data('type');
            var points = selectedOption.data('points');
            
            // Fill in the form fields
            $inline.find('textarea[name*="question_text"], input[name*="question_text"]').val(questionText);
            $inline.find('select[name*="question_type"]').val(questionType);
            $inline.find('input[name*="points"]').val(points);
            
            // Show success message after the dropdown
            $select.closest('.copy-from-dropdown').after(
                '<div class="reuse-info" style="background: #d4edda; color: #155724; border-left: 4px solid #28a745;">' +
                '<strong>Question Copied!</strong> Fields have been auto-filled. After saving, you can edit the question to add/modify answer choices.' +
                '</div>'
            );
        }
    }
    
    function escapeHtml(text) {
        if (!text) return '';
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML.replace(/"/g, '&quot;');
    }
    
})(django.jQuery || jQuery);

