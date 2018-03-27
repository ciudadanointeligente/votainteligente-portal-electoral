var ligaCidades = function(componenteBusca, selecionaValores) {
  cBusca = $( componenteBusca );
  cBusca.autocomplete({
    source: function( request, response ) {
      $.ajax({
          url: "/cities?match=" + request.term
          , method: "get"
          , accept: "application/json"
          , success: function( data ) {
              var objetos  = data.map(function(cidade){
                  return {
                      value: cidade[0]
                      , label: cidade[1]
                  };
              });
              response( data.length === 1 && data[ 0 ].length === 0 ? [] : objetos );
          }
          , error: function(xref) {
            selecionaValores(xref);
          }
        });
    }
    , minLength: 2
    , select: function( event, ui ) {
      cBusca.val(ui.item.label);
      return false;
    }
    , change: function( event, ui ) {
      if (ui.item != null) {
        var retorno = {
          id: ui.item.value
          , texto: ui.item.label
        };
        cBusca.val(ui.item.label);
        selecionaValores(null, retorno);
      }
      else {
        cBusca.val('');
        selecionaValores(null, {});
      }
      return false;
    }
    , focus: function( event, ui ) {
      event.preventDefault();
      $(event.target).val(ui.item.label);
    }
  } );
};
