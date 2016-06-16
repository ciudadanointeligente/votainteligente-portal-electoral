var gulp = require('gulp'),
    shell = require('gulp-shell'),
    watch = require('gulp-watch'),
    gutil = require('gulp-util');

gulp.task('runserver', shell.task(['python manage.py runserver']));

gulp.task('compile_scss', function () {
    watch('votai_general_theme/static/sass/**/*.scss', function () {
        shell.task(['python manage.py compilescss']);
        gutil.log('Compilando Scss');
    });
});

gulp.task('default', ['runserver', 'compile_scss']);
