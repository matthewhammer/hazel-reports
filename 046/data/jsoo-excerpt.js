         rest$1 = arcs[2],
         a$0 = arcs[1],
         i$14 =  /*<<petri.ml:12:63>>*/ a$0[1];
        c:
        {
         d:
         {
          var xs = xs$0, i$10 = i$14, _bN_ = a$0[2];
          for(;;){
            /*<<petri.ml:9:19>>*/ if(! xs) break;
           var rest = xs[2], x$0 = xs[1];
            /*<<petri.ml:9:56>>*/ if(0 === i$10) break d;
           var i$11 =  /*<<petri.ml:9:77>>*/ i$10 - 1 | 0;
           xs = rest;
           i$10 = i$11;
          }
          var _bO_ =  /*<<petri.ml:9:39>>*/ 0;
          break c;
         }
         var _bO_ =  /*<<petri.ml:9:70>>*/ x$0;
        }
        var _bP_ =  /*<<petri.ml:12:76>>*/ _bN_ <= _bO_ ? 1 : 0;
        if(! _bP_) break b;
        arcs = rest$1;
       }
       var _bS_ =  /*<<petri.ml:12:43>>*/ 1;
       break a;
      }
      var _bS_ =  /*<<petri.ml:13:18>>*/ _bP_;
     }
      /*<<petri.ml:22:36>>*/ if(_bS_)
      var
       _bQ_ =  /*<<petri.ml:18:41>>*/ puts(t$1[3], 0),
       _bR_ =  /*<<petri.ml:18:26>>*/ takes(t$1[2], _bQ_),
       cmd =  /*<<petri.ml:18:62>>*/ [2, t$1[1], _bR_];
     else
      var
       s1 =  /*<<petri.ml:22:54>>*/ t$1[1],
       cmd =  /*<<petri.ml:22:86>>*/ [2, s1 + " cannot fire now", 0];
    }
    else
     var
      s2 =  /*<<stdlib.ml:266:2>>*/ "" + i$16,
      cmd =  /*<<petri.ml:21:60>>*/ [2, "there is no transition " + s2, 0];
