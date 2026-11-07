    _dw_ =
      [0,
       [1, "320"],
       [0,
        [2, "440"],
        [0,
         [3,
          [0,
           [0, "border", "1px solid #ccc"],
           [0, [0, "background", "#fafafa"], 0]]],
         0]]],
    _dx_ = "viewBox",
    _dy_ = "svg",
    _dz_ =
      [1,
       [0,
        [3,
         [0,
          [0, "font-family", "var(--code-font)"],
          [0, [0, "font-size", "0.8em"], 0]]],
        0],
       [0, [2, "no picture yet"], 0]],
    _dt_ = [0, 0., 0., 0., 0.],
    _du_ = [0, 0., 0., 0., 0.],
    _dg_ = [0, [0, cst_stroke_linejoin, cst_round], 0],
    _dh_ = cst_stroke_width,
    _di_ = cst_stroke,
    _dj_ = cst_fill,
    _dk_ = cst_points,
    _dl_ = "polygon",
    _dm_ =
      [0,
       [0, cst_stroke_linejoin, cst_round],
       [0, [0, "stroke-linecap", cst_round], 0]],
    _dn_ = cst_stroke_width,
    _do_ = cst_stroke,
    _dp_ = [0, cst_fill, cst_none],
    _dq_ = cst_points,
    _dr_ = "polyline",
    _dd_ = [0, [8, [0, 0, 0], 0, [0, 1], 0], "%.1f"],
    _dO_ =
      [0,
       [11,
        '{"label": "jsoo", "median_ms": ',
        [8,
         [0, 0, 0],
         0,
         [0, 4],
         [11,
          ', "min_ms": ',
          [8,
           [0, 0, 0],
           0,
           [0, 4],
           [11, ', "chars": ', [4, 0, 0, 0, [11, "}\n", 0]]]]]]],
       '{"label": "jsoo", "median_ms": %.4f, "min_ms": %.4f, "chars": %d}\n'],
    _c9_ = caml_obj_tag(_c$_) === 248 ? _c$_ : _c$_[1];
   caml_register_named_value("jsError", _c9_);
   (function(exn){throw exn;});
   var _da_ = globalThis;
   _da_.String;
   _da_.RegExp;
   _da_.Object;
   _da_.Date;
   _da_.Math;
   _da_.Error;
   _da_.JSON;
   var _db_ = _da_.Array;
   _c2_
    (function(_fd_){
      return _fd_[1] === _c__
              ? [0, caml_string_of_jsstring(_fd_[2].toString())]
              : 0;
     });
   _c2_
    (function(_fc_){
      return _fc_ instanceof _db_
              ? 0
              : [0, caml_string_of_jsstring(_fc_.toString())];
     });
   function _dc_(_fb_){return caml_call1(_cx_(_dd_), _fb_);}
   function _de_(_e9_){
    if(! _e9_) return _df_;
    var
     _e__ = _e9_[1][1],
     _fa_ = cst$4 + _de_(_e9_[2]),
     _e$_ = "," + _dc_(_e__[2]) + _fa_;
    return _dc_(_e__[1]) + _e$_;
   }
   function _ds_(_e4_){
    if(_e4_){
     var _e5_ = _ds_(_e4_[2]), _e6_ = _e4_[1];
     if(0 === _e6_[0])
      var
       _e0_ = [0, [0, _dh_, _dc_(_e6_[3][1])], _dg_],
       _e1_ = [0, [0, _dj_, _e6_[4]], [0, [0, _di_, _e6_[3][2]], _e0_]],
       _e7_ = [0, _dl_, [0, [0, _dk_, _de_(_e6_[2])], _e1_], 0];
     else
      var
       _e2_ = [0, [0, _dn_, _dc_(_e6_[3][1])], _dm_],
       _e3_ = [0, _dp_, [0, [0, _do_, _e6_[3][2]], _e2_]],
       _e7_ = [0, _dr_, [0, [0, _dq_, _de_(_e6_[2])], _e3_], 0];
     var _e8_ = [0, _e7_, _e5_];
    }
    else
     var _e8_ = _e4_;
    return _e8_;
   }
   function _dv_(_eU_){
    if(! _eU_) return _dz_;
    var _eV_ = _eU_[1];
    a:
    {
     b:
     {
      var _eE_ = _eV_, _eW_ = _ds_(_eV_);
      for(;;){
       if(! _eE_) break;
       var _eF_ = _eE_[2], _eG_ = _eE_[1];
       if(0 === _eG_[0])
        _eE_ = _eF_;
       else{if(_eG_[1] === cst_frame) break b; _eE_ = _eF_;}
      }
      var _eH_ = _eE_;
      break a;
     }
     var _eH_ = [0, _eG_, 0];
    }
    var _eI_ = _eH_ || _eV_;
    if(_eI_){
     var _em_ = _eI_[1][2];
     if(_em_)
      var
       _eJ_ = _em_[1][1],
       _eK_ = _eJ_[2],
       _eL_ = _eJ_[1],
       _eM_ = [0, _eL_, _eK_, _eL_, _eK_];
     else
      var _eM_ = _dt_;
     var _eN_ = _eM_;
    }
    else
     var _eN_ = _du_;
    var _eC_ = _eN_, _eB_ = _eI_;
    for(;;){
     if(! _eB_) break;
     var _ez_ = _eC_, _ey_ = _eB_[1][2], _eD_ = _eB_[2];
     for(;;){
      if(! _ey_) break;
      var
       _en_ = _ez_[4],
       _eo_ = _ez_[3],
       _ep_ = _ez_[2],
       _eq_ = _ez_[1],
       _er_ = _ey_[1][1],
       _es_ = _er_[2],
       _et_ = _er_[1],
       _eA_ = _ey_[2],
       _eu_ = _en_ < _es_ + 12. ? _es_ + 12. : _en_,
       _ev_ = _eo_ < _et_ + 12. ? _et_ + 12. : _eo_,
       _ew_ = _es_ - 12. < _ep_ ? _es_ - 12. : _ep_,
       _ex_ = _et_ - 12. < _eq_ ? _et_ - 12. : _eq_;
      _ez_ = [0, _ex_, _ew_, _ev_, _eu_];
      _ey_ = _eA_;
     }
     _eC_ = _ez_;
     _eB_ = _eD_;
    }
    var
     _eO_ = _eC_[2],
     _eP_ = _eC_[1],
     _eQ_ = _eC_[4] - _eO_,
     _eR_ = _eC_[3] - _eP_;
    if(_eQ_ * 320. < _eR_ * 440.)
     var _eT_ = _eR_ * 440. / 320., _eS_ = _eR_;
    else
     var _eT_ = _eQ_, _eS_ = _eQ_ * 320. / 440.;
    var
     _eZ_ = cst$4 + _dc_(_eT_),
     _eY_ = cst$4 + _dc_(_eS_) + _eZ_,
     _eX_ = cst$4 + _dc_(_eO_ - (_eT_ - _eQ_) / 2.) + _eY_;
    return [0,
            _dy_,
            [0, [0, _dx_, _dc_(_eP_ - (_eS_ - _eR_) / 2.) + _eX_], _dw_],
            _eW_];
   }
