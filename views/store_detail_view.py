from flask import Blueprint, render_template, request, url_for, session, redirect, flash
from models.models import *
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('store_detail', __name__, url_prefix="/store")

#가게 정보를 보여줄 것
@bp.route('/<int:store_id>')
def store_detail(store_id):
    
    #store 테이블에서 정보를 몽땅 가져오자
    #reveiw review테이블에서 따로 관리되고 있기 때문에 여기서 정보를 또 다 가져와야함
    
    #filter_by는 매개변수로 넘기는 느낌. not, like, or 같은 것과 함께 쓸 수 없음
    #filter( User.id==user_id) 과 같이 이름도 써야하고, 조건문으로 넘기는 느낌.
    store_info = rabbitStore.query.filter_by(id=store_id).first() #객체에서 반환값을 뽑기위해 first, all등을 사용해야 한다!
    review_info = rabbitReview.query.filter(rabbitReview.store_id==store_id).all()
    menu_info = rabbitMenu.query.filter_by(store_id=store_id).all()

    #언제나 검증하는 과정을 꼭 거치자!
    if not store_info: #store_info가 존재하지 않는 값이 들어가서 noneType이면
        flash("잘못된 접근입니다.")
        return redirect(url_for('main.home')) #혹은 에러페이지를 만들어서 에러페이지로 보내자

    rating_sum, average=0,0
    if review_info: #review가 한개라도 존재한다면
        for review in review_info:
            rating_sum += review.rating
        average = rating_sum / len(review_info)

    return render_template("store_detail.html", store_info=store_info, review_info=review_info, menu_info=menu_info, avg=average)

#리뷰를 쓰니까 -> 작성할 수 있는 POST를 받는 걸 만들 것
@bp.route('/write_review/<int:store_id>', methods = ['POST'])
def create_review(store_id):
    if 'user_id' not in session:
        flash("권한이 없습니다")
        return redirect(url_for('main.home' ))
    
    user_id = session['user_id']
    
    rating = request.form['star']
    content = request.form['review']

    #init이 없으므로 대입해서 넣어주는 것이 좋다
    review=rabbitReview(user_id=user_id, store_id=store_id, rating=rating, content=content)
    db.session.add(review)
    db.session.commit()

    flash("리뷰가 작성되었습니다")
    return redirect(url_for("store_detail.store_detail", store_id=store_id))

# 리뷰를 삭제할 수 도 있음 -> 삭제 요청을 받는 걸 만들어야 함
@bp.route('/delete_review/<int:review_id>')
def delete_review(review_id):
    if 'user_id' not in session:
        flash("권한이 없습니다")
        return redirect(url_for('main.home'))
    
    user_info=rabbitUser.query.filter_by(id=session['user_id']).first()
    review_info=rabbitReview.query.filter_by(id=review_id).first()
    
    if not review_info:
        flash("잘못된 접근입니다.")
        return redirect(url_for('main.home'))

    if not user_info or review_info.user_id != session['user_id']:
        flash("권한이 없습니다.")
        return redirect(url_for('main.home'))

    db.session.delete(review_info)
    db.session.commit()

    flash("정상적으로 삭제 되었습니다.")
    
    store_info = rabbitStore.query.filter_by(id=review_info.store_id).first()
    return redirect(url_for("store_detail.store_detail", store_id=store_info.id))