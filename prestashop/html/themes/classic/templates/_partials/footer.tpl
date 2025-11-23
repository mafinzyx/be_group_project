{**
 * Copyright since 2007 PrestaShop SA and Contributors
 * PrestaShop is an International Registered Trademark & Property of PrestaShop SA
 *
 * NOTICE OF LICENSE
 *
 * This source file is subject to the Academic Free License 3.0 (AFL-3.0)
 * that is bundled with this package in the file LICENSE.md.
 * It is also available through the world-wide-web at this URL:
 * https://opensource.org/licenses/AFL-3.0
 * If you did not receive a copy of the license and are unable to
 * obtain it through the world-wide-web, please send an email
 * to license@prestashop.com so we can send you a copy immediately.
 *
 * DISCLAIMER
 *
 * Do not edit or add to this file if you wish to upgrade PrestaShop to newer
 * versions in the future. If you wish to customize PrestaShop for your
 * needs please refer to https://devdocs.prestashop.com/ for more information.
 *
 * @author    PrestaShop SA and Contributors <contact@prestashop.com>
 * @copyright Since 2007 PrestaShop SA and Contributors
 * @license   https://opensource.org/licenses/AFL-3.0 Academic Free License 3.0 (AFL-3.0)
 *}
<div class="container">
  <div class="row">
    {block name='hook_footer_before'}
      {hook h='displayFooterBefore'}
    {/block}
  </div>
</div>
<div class="footer-container dobrewina-footer">
  <div class="container">
    <div class="row">
      <div class="col-md-3 col-sm-6">
        <h4>WG RODZAJU WINA</h4>
        <ul>
          <li><a href="#">Wina czerwone</a></li>
          <li><a href="#">Wina białe</a></li>
          <li><a href="#">Wina różowe</a></li>
          <li><a href="#">Wina musujące</a></li>
          <li><a href="#">Wina bezalkoholowe</a></li>
          <li><a href="#">Wina wegańskie</a></li>
          <li><a href="#">Wina wzmacniane</a></li>
        </ul>
      </div>
      <div class="col-md-3 col-sm-6">
        <h4>WG POCHODZENIA WINA</h4>
        <ul>
          <li><a href="#">Wina włoskie</a></li>
          <li><a href="#">Wina portugalskie</a></li>
          <li><a href="#">Wina polskie</a></li>
          <li><a href="#">Wina francuskie</a></li>
          <li><a href="#">Wina hiszpańskie</a></li>
          <li><a href="#">Wina niemieckie</a></li>
        </ul>
      </div>
      <div class="col-md-3 col-sm-6">
        <h4>WARSZTATY WINIARSKIE</h4>
        <ul>
          <li><a href="#">O nas - Warsztaty</a></li>
          <li><a href="#">Nasze warsztaty</a></li>
          <li><a href="#">Warsztaty dla firm</a></li>
          <li><a href="#">Prywatne imprezy</a></li>
        </ul>
      </div>
      <div class="col-md-3 col-sm-6">
        <h4>ZAKUPY</h4>
        <ul>
          <li><a href="#">Krok po kroku</a></li>
          <li><a href="#">Jak czytać legendę</a></li>
          <li><a href="#">Sposób płatności</a></li>
          <li><a href="#">Sposób odbioru / realizacji</a></li>
          <li><a href="#">Klub dobrewina.pl</a></li>
          <li><a href="#">Kontakt</a></li>
        </ul>
      </div>
    </div>
    <div class="row">
      {block name='hook_footer'}
        {hook h='displayFooter'}
      {/block}
    </div>
    <div class="row">
      {block name='hook_footer_after'}
        {hook h='displayFooterAfter'}
      {/block}
    </div>
    <div class="row">
      <div class="col-md-12">
        <div class="footer-contact">
          <p><strong>Dobre Wina Sp. z o.o.</strong></p>
          <p>+48 664 159 023</p>
          <p>sklep@dobrewina.pl</p>
          <p>ul. Wyczółki 46, 02-820 Warszawa, Polska</p>
        </div>
        <p class="text-sm-center footer-copyright">
          {block name='copyright_link'}
            <a href="#" target="_blank" rel="noopener noreferrer nofollow">
              © Copyright - {date('Y')}
            </a>
          {/block}
        </p>
        <p class="text-sm-center footer-links">
          <a href="#">Polityka prywatności</a> | 
          <a href="#">Regulamin</a> | 
          <a href="#">Mapa strony</a> | 
          <a href="#">Blog</a>
        </p>
      </div>
    </div>
  </div>
</div>
