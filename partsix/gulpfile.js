const gulp = require('gulp');
const rigger = require('gulp-rigger');

gulp.task('build', function() {
  return gulp.src('header.html') // Замените 'src/*.html' путем к вашим исходным файлам
    .pipe(rigger())
    .pipe(gulp.dest('dist')); // Замените 'dist' путем к вашему выходному каталогу
});

// Добавьте другие задачи Gulp, если необходимо
