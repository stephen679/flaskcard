$(document).ready(function() {
  $("#extendable").click(function() {
    var nextField = parseInt($(".extendable-field").last().attr("name").split("-").pop()) + 1;
    var newDiv = "<div class='extendable-field' name='extendable-" + nextField + "'>";
    newDiv += "<span> Category Name: </span><input type='text' name='category-" + nextField + "'/>";
    newDiv += "<span> Weight: </span><input type='text' weight='weight-" + nextField + "' /></br></div>";
    console.log(newDiv);
    $(newDiv).appendTo(".extendable-form");
  });
});
