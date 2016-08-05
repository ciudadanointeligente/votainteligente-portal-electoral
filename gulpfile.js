var gulp = require('gulp'),
    shell = require('gulp-shell'),
    watch = require('gulp-watch'),
    gutil = require('gulp-util');

gulp.task('watch_compilescss', function () {
    shell.task(['python manage.py compilescss'])
    watch('votai_general_theme/static/sass/**/*.scss', function (vynil) {
                                               gulp.src('votai_general_theme/static/sass/**/*.scss')
                                                   .pipe(shell(['python manage.py compilescss',]));
    });
});

gulp.task('default', ['watch_compilescss']);
