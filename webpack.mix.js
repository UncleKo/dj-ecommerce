const mix = require('laravel-mix');

/*
 |--------------------------------------------------------------------------
 | Mix Asset Management
 |--------------------------------------------------------------------------
 |
 | Mix provides a clean, fluent API for defining some Webpack build steps
 | for your Laravel application. By default, we are compiling the Sass
 | file for the application as well as bundling up all the JS files.
 |
 */

mix
    .js('resources/js/app.js', 'static_files/js').react()
    // .sass('resources/scss/blog.scss', 'static_files/css')
    .sass('resources/scss/styles.scss', 'static_files/css')
    .sourceMaps(true, 'inline-source-map')
    .options({
        postCss: [
            require('autoprefixer')({
                browsers: ['>1%'],
                grid: true
            })
        ]
    })
    .browserSync({
        files: "static_files/**, templates/**",
        // files: "*.html, css/*.css",
        // browser: 'Firefox',
        proxy: 'http://127.0.0.1:8000/'
        //   server: { baseDir: ['public'] }
    })
    .disableNotifications();

