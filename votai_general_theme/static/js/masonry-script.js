// Load is used to ensure all images have been loaded, impossible with document

jQuery(window).load(function () {



  // Takes the gutter width from the bottom margin of .post

  var gutter = parseInt(jQuery('.post').css('marginBottom'));
  var container = jQuery('#posts');



  // Creates an instance of Masonry on #posts

  container.masonry({
    gutter: gutter,
    itemSelector: '.post',
    columnWidth: '.post'
  });
  
  
  
  // This code fires every time a user resizes the screen and only affects .post elements
  // whose parent class isn't .container. Triggers resize first so nothing looks weird.
  
  jQuery(window).bind('resize', function () {
    if (!jQuery('#posts').parent().hasClass('container')) {
      
      
      
      // Resets all widths to 'auto' to sterilize calculations
      
      post_width = jQuery('.post').width() + gutter;
      jQuery('#posts, body > #grid').css('width', 'auto');
      
      
      
      // Calculates how many .post elements will actually fit per row. Could this code be cleaner?
      
      posts_per_row = jQuery('#posts').innerWidth() / post_width;
      floor_posts_width = (Math.floor(posts_per_row) * post_width) - gutter;
      ceil_posts_width = (Math.ceil(posts_per_row) * post_width) - gutter;
      posts_width = (ceil_posts_width > jQuery('#posts').innerWidth()) ? floor_posts_width : ceil_posts_width;
      if (posts_width == jQuery('.post').width()) {
        posts_width = '100%';
      }
      
      
      
      // Ensures that all top-level elements have equal width and stay centered
      
      jQuery('#posts, #grid').css('width', posts_width);
      jQuery('#grid').css({'margin': '0 auto'});
            
    
    
    }
  }).trigger('resize');
  


});