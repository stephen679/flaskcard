$(document).ready(function() {
  $("#extendable").click(function() {
    var nextField = parseInt($(".extendable-field").last().attr("name").split("-").pop()) + 1;
    var newDiv = "<div class='extendable-field' name='extendable-" + nextField + "'>";
    newDiv += "<p> <label>Category Name: </label> <input type='text' name='category-" + nextField + "'/></p>";
    newDiv += "<p> <label>Weight: </label><input type='text' name='weight-" + nextField + "' /></p></br></div>";
    console.log(newDiv);
    $(newDiv).appendTo(".extendable-form");
  });
});
