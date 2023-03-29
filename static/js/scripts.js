// marks off completed to-do list task
function toggleCompleted(id) {
    const todoCells = document.querySelectorAll(`#todo-${id} td`);
    todoCells.forEach(cell => {
      if (cell.classList.contains('completed')) {
        cell.classList.remove('completed');
      } else {
        cell.classList.add('completed');
      }
    });
  }

//confirmation pops up when delete button is selected to delete an item
function confirmDelete() {
    return confirm("Are you sure you want to delete this item from your To-Do list?");
  }
