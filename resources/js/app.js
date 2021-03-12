import { $, $$ } from './components/bling.js';
import React from 'react';
import ReactDOM from 'react-dom';
import PhotoInsert from './PhotoInsert';

if (document.querySelector('.photo_insert')) {
  ReactDOM.render(<PhotoInsert />, document.querySelector('.photo_insert'));
}

(function ($, $$) {

  const navbarCollapseFunction = () => {

    let triggers = $$('.navbar-toggler-icon')
    let navbars = $$('.navbar-collapse')

    function navbarToggle(i, e) {
      navbars[i].classList.toggle('collapse');
    }
    triggers.forEach((trigger, i) => trigger.on('click', navbarToggle.bind(event, i)));

    // navbarToggler.on('click', function () {
    //   navbarCollapse.classList.toggle('collapse');
    // })

    // document.body.on('click', function (e) {
    //   // if(!e.target.classList.contains('navbar-toggler-icon')) {
    //   if (e.target !== navbarToggler) {
    //     navbarCollapse.classList.add('collapse');
    //   }
    // })

  } //navbarCollapseFunction

  navbarCollapseFunction();


  if ($('#id_featured_image')) {
    $('#id_featured_image').on('change', function () {
      let filename = this.value.replace(/^.*[\\\/]/, '')
      $('#label_for_featured_image').innerHTML = filename;
    })
  }


  const multiFormControl = () => {

    // 画像アップロードフォームにて、2番目以降のフォームを隠す（１個だけ表示する）
    const hideOthers = (elem) => {
      let el = document.querySelectorAll(elem);
      for (let i = 1; i < el.length; i++) {
        el[i].classList.add('hide');
        el[0].classList.add('mt-0');
      }
    } // hideOthers

    // hideOthers('link-form'); //Post新規投稿ページ =>下記functionに統一=>
    hideOthers('.photo-form .multiField'); //Photo Upload Page
    // hideOthers('.item-form .multiField'); //Item Create Page


    // クリックで１個ずつフォームの表示・非表示
    const toggleForms = (elem) => {
      let el = document.querySelectorAll(elem);
      let i = 1;
      if ($('#add-form')) {
        $('#add-form').on('click', function (e) {
          e.preventDefault();
          el[i].classList.remove('hide');
          i++;
        })
      }

      if ($('#remove-form')) {
        $('#remove-form').on('click', function (e) {
          i > 1 ? i-- : i;
          e.preventDefault();
          el[i].classList.add('hide');
        })
      }
    } // toggleForms

    // toggleForms('link-form'); //Post新規投稿ページ =>下記functionに統一=>
    toggleForms('.photo-form .multiField'); //Photo Upload Page
    // toggleForms('.item-form .multiField');  //Item Create Page


    // 既にデータが入ってるフォームのみ表示
    function hideEmptyForms1(elem) {
      let linkForms = document.querySelectorAll(elem);
      linkForms.forEach(form => {
        let urlinput = form.querySelector('.urlinput');
        if (urlinput.value == "" || urlinput.value == null) {
          //空のフォームを非表示、表示/非表示をコントロール、"削除する"チェックボックスを非表示にする->SCSS
          form.classList.add('hide', 'togglable', 'url-empty');
        }
      });
      // PostにURLがひとつもない場合(新規投稿含む)、ひとつだけ空のフォームを表示
      let el = document.querySelectorAll('.no-urls .togglable')[0];
      if (el) {
        el.classList.remove('hide');
      }

      toggleForms('.togglable');
    } //hideEmptyFormas

    hideEmptyForms1('.link-form');


    function hideEmptyForms2(elem) {
      let imgForms = document.querySelectorAll(elem);
      imgForms.forEach(form => {
        if (!form.getElementsByTagName('a').length) {
          form.classList.add('hide', 'togglable', 'img-empty');
        }
      })
      // // ひとつだけ空のフォームを表示
      // document.querySelectorAll('.togglable')[0].classList.remove('hide');
      // Itemにその他画像がひとつもない場合(新規投稿含む)のみ、ひとつだけ空のフォームを表示
      let el = document.querySelectorAll('.no-data .togglable')[0];
      if (el) {
        el.classList.remove('hide');
      }

      toggleForms('.togglable');
    }
    hideEmptyForms2('.item-form .multiField');

  } //multi_form_control


  multiFormControl()


  const imageFormThumbs = () => {

    let mainImgLink = document.querySelector('#div_id_image a');

    // let imgSrc = mainImgLink.getAttribute('href');
    // let containDiv = document.createElement('div');
    // containDiv.setAttribute('class', 'thumb-wrap');
    // containDiv.innerHTML = `<img src="${imgSrc}">`;
    // mainImgLink.parentNode.insertBefore(containDiv, mainImgLink.parentNode.firstChild);

    let mainImgThumb = document.querySelector('#main-thumb');
    mainImgLink.parentNode.insertBefore(mainImgThumb, mainImgLink.parentNode.firstChild);


    let otherImgLinks = document.querySelectorAll('.photo-formset .multiField a');
    let otherImgThumbs = document.querySelectorAll('.thumb-container img')

    otherImgLinks.forEach((link, i) => {
      // let imgSrc = link.getAttribute('href');
      let containDiv = document.createElement('div');
      containDiv.setAttribute('class', 'thumb-wrap');
      // // let imgThumb = document.createElement('img');
      // // imgThumb.setAttribute('src', `${imgSrc}`);
      // containDiv.innerHTML = `<img src="${imgSrc}">`;
      // link.parentNode.insertBefore(containDiv, link.parentNode.firstChild);
      containDiv.appendChild(otherImgThumbs[i]);
      link.parentNode.insertBefore(containDiv, link.parentNode.firstChild);
    })

  }

  imageFormThumbs();


  const modalControl = () => {

    let modals = $$('.modal');

    function expandModal(i, e) {
      modals[i].classList.add('show-modal');
    }

    function closeModal(i, e) {
      if (!e.target.classList.contains('keep-modal')) {
        modals[i].classList.remove('show-modal');
        // modals.forEach(modal => () => {
        //   modal.classList.remove('show-modal');
        // })
      }
    }

    let trigers = $$('.expand-modal');
    if ($('.expand-modal')) {
      trigers.forEach((triger, i) => triger.on('click', expandModal.bind(event, i)));
      // $('.expand-modal').on('click', expandModal);
    }

    // modal.on('click', closeModal);
    modals.forEach((modal, i) => modal.on('click', closeModal.bind(event, i)));


  } // modal_control

  if ($('.modal')) {
    modalControl();
  }


  const makeSquare = () => {

    let squares = $$('.square');

    squares.forEach((square) => {
      console.log(square.offsetWidth);
      square.style.height = square.offsetWidth + 'px';
    });

  }

  if ($('.square')) {
    makeSquare();
  }



  // // Without bing.js
  // let modal = document.querySelector('.modal');
  // let photos = document.querySelectorAll('#photos img');

  // function insertImage() {
  //   let image = '<a href="' + this.dataset.origin + '"><img src="' + this.dataset.medium + '"></a>';
  //   document.querySelector('#id_content').value += image;
  // }

  // function expandModal() {
  //   modal.classList.add('show');
  // }

  // function closeModal(e) {
  //   // console.log(e);
  //   // if(e.target==='form') return;
  //   modal.classList.remove('show');
  // }

  // photos.forEach( photo => photo.addEventListener('click', insertImage));

  // document.querySelector('#expand-modal').addEventListener('click', expandModal);

  // modal.addEventListener('click', closeModal);

})($, $$);