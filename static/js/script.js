const maxHeight = Array.from(document.getElementsByClassName("max-height"));
const cards = Array.from(document.getElementsByClassName("card"));
const forms = Array.from(document.getElementsByTagName("form"));
const formCopyBtns = document.getElementsByClassName("form-copy-btn");

function updateMaxHeight(elem) {
  let prevElem = elem.previousElementSibling;
  let prevElemHeight = prevElem.offsetHeight;
  let height = window.innerHeight - prevElemHeight;
  elem.style.height = `${height}px`;
}

if (maxHeight) {
  maxHeight.map((elem) => {
    updateMaxHeight(elem);
  });

  window.onresize = () => {
    maxHeight.map((elem) => {
      updateMaxHeight(elem);
    });
  };
}

if (cards) {
  cards.map((item) => {
    item.addEventListener("mouseenter", (e) =>
      e.target.classList.toggle("shadow")
    );
    item.addEventListener("mouseleave", (e) =>
      e.target.classList.toggle("shadow")
    );
  });
}

if (forms) {
  forms.map((item) => {
    Array.from(item).map((field) => {
      switch (field.tagName.toLowerCase()) {
        case "input":
          switch (field.type) {
            case "submit":
              field.classList.add("btn");
              break;
            case "checkbox":
              field.classList.add("form-check-input");
              break;
            default:
              field.classList.add("form-control");
              break;
          }

          break;

        case "select":
          field.classList.add("form-select");
          break;

        case "textarea":
          field.classList.add("form-control");
          break;

        default:
          break;
      }
    });
  });
}

function copyForm(source, dest, exclude = []) {
  let sourceFormElements = getFormElements(source);
  let destFormElements = getFormElements(dest);

  sourceFormElements.forEach((itemOne) => {
    destFormElements.map((itemTwo) => {
      if (itemOne.name === itemTwo.name && !exclude.includes(itemOne.name)) {
        let value = itemOne.value;
        itemTwo.value = value;
      }
    });
  });
}

function resetForm(form, exclude = []) {
  let formElements = Array.from(form);
  formElements.forEach((item) => {
    if (!(item.name in exclude)) {
      item.value = "";
    }
  });
}

function getFormElements(parentElement) {
  if (parentElement.tagName.toLowerCase() === "form") {
    return parentElement.elements;
  }

  let validFormElements = [
    "input",
    "label",
    "select",
    "textarea",
    "button",
    "fieldset",
    "legend",
    "datalist",
    "output",
    "option",
    "optgroup",
  ];
  let allElements = [];
  let validElements = [];

  validFormElements.forEach((name) => {
    let elements = parentElement.getElementsByTagName(name);
    allElements.push(elements);
  });

  allElements.forEach((elemCollection) => {
    Array.from(elemCollection).forEach((elem) => {
      if (validFormElements.includes(elem.tagName.toLowerCase())) {
        validElements.push(elem);
      }
    });
  });

  return validElements;
}

function disableAllElements(parentElement) {
  get(parentElement).map((item) => {
    item.disabled = true;
  });
}

// Form copy
if (formCopyBtns) {
  let btns = Array.from(formCopyBtns);
  btns.map((btn) => {
    btn.addEventListener("change", (e) => {
      let source = document.querySelector(
        e.target.getAttribute("data-copy-source")
      );
      let destination = document.querySelector(
        e.target.getAttribute("data-copy-destination")
      );
      let exclude = e.target.getAttribute("data-copy-exclude");
      if (e.target.checked) {
        getFormElements(destination).map((item) => {
          item.disabled = true;
        });
        copyForm(source, destination, (exclude = [exclude]));
      } else {
        getFormElements(destination).map((item) => {
          item.disabled = false;
        });
        resetForm(shippingForm, (exclude = [exclude]));
      }
    });
  });
}
