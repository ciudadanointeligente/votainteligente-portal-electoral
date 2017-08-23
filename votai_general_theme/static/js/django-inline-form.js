/*
  django-inline-formset.js

  @author Benjamin W Stookey

  https://github.com/jamstooks/jquery-django-inline-form
*/
!function($) {

  $.fn.djangoInlineFormAdd = function(options) {

    if(options.prefix != undefined) {
      this.prefix = options.prefix;
      this.containerId = '#' + this.prefix + '-container';
      this.templateId = '#' + this.prefix + '-template';
      this.totalFormsId = '#id_' + this.prefix + '-TOTAL_FORMS';
      this.maxFormsId = '#id_' + this.prefix + '-MAX_NUM_FORMS';
      this.deleteButtonId = '#' + this.prefix + '-delete';
    }
    else {
      if( options.containerId == undefined ||
          options.templateId == undefined ||
          options.totalFormsId == undefined ||
          options.maxFormsId == undefined
      ){
        console.error("[djangoInlineForm] if prefix is not provided in options, containerId, templateId, totalFormsId, and maxFormsId must be");
        return;
      }
    }
    // even if a prefix is defined, ids may change
    this.containerId = options.containerId != undefined ? options.containerId : this.containerId;
    this.templateId = options.templateId != undefined ? options.templateId : this.templateId;
    this.totalFormsId = options.totalFormsId != undefined ? options.totalFormsId : this.totalFormsId;
    this.maxFormsId = options.maxFormsId != undefined ? options.maxFormsId : this.maxFormsId;
    this.deleteButtonId = options.deleteButtonId != undefined ? options.deleteButtonId : this.deleteButtonId;

    this.postClick = options.postClick != undefined ? options.postClick : null;
    this.formHeight = options.formHeight != undefined ? options.formHeight : null;

    var max = $(this.maxFormsId).attr('value');

    var self = this;

    this.addForm = function(ev) {
      ev.preventDefault();
      var count = $(self.containerId).children('fieldset').length+1;
      if (count >= max) {
        console.log('exceeded max inline forms');  // should maybe have a callback option
        return;
      }
      var tmplMarkup = $(self.templateId).html();
      var compiledTmpl = tmplMarkup.replace(/__prefix__/g, count);
      $(self.containerId).append(compiledTmpl);

      // run postClick method
      if (self.postClick != null) { self.postClick(); }

      // animate it
      $(self.containerId).children().last().show('slow');

      // update form count
      $(self.totalFormsId).attr('value', count+1);

      // some animate to scroll to view our new form
      if(self.formHeight != null) {
        $('html, body').animate({
          scrollTop: $(window).scrollTop() + self.formHeight
        }, 800);
      }
    };

    this.removeForm = function(ev) {
      $(self.containerId).children().last().hide('slow', function(){
        $(self.containerId).children().last().remove();
        $(self.totalFormsId).attr('value', $(self.containerId).children().length);
      });
      // some animate to scroll up
      if(self.formHeight != null) {
        $('html, body').animate({
          scrollTop: $(window).scrollTop() - self.formHeight
        }, 800);
      }
    }

    this.click(this.addForm);
    if(this.deleteButtonId != null) {
      $(this.deleteButtonId).click(this.removeForm);
    }
  }
}(window.jQuery);
